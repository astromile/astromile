import numpy as np
import scipy.optimize as opt

import heston

class IRCurve:
	def df(self,t):
		raise NotImplementedError()

class ZeroCurve(IRCurve):
	def df(self,t):
		return np.exp(-t*self.zeroRate(t))

	def zeroRate(self,t):
		raise NotImplementedError()

class Interpolator:
	def __init__(self,x,y):
		self.x = np.array(x)
		self.y = np.array(y)

	def locate(self,x):
		if x<=self.x[0]:
			return (0,1)
		elif x>=self.x[-1]:
			n = len(self.x)
			return (n-2,n-1)
		else:
			left = bisect.bisect_right(x,a)
			return (left,left+1)

	def __call__(self,x):
		raise NotImplementedError()

class InterpolatedZeroCurve(ZeroCurve):
	def __init__(self,interpolator):
		self.interpolator = interpolator

	def zeroRate(self,t):
		return self.interpolator(t)

class LinearInterpolator(Interpolator):
	def __init__(self,x,y):
		super(LinearInterpolator).__init__(self,x,y)

		if len(x)>1:
			self.dx = x[1:]-x[:-1]
			self.fx = (y[1:]-y[:-1])/self.dx

	def __call__(self,x):
		if len(self.x)==1:
			return self.y[0]
		elif len(self.x)>1:
			left, right = self.locate(x)
			return self.y[left] + self.fx[left] * (x - self.x[left]) / self.dx[left]

class ForwardCurve:
	def __init__(self,spot,domCurve,forCurve):
		self.spot = spot
		self.domCurve = domCurve
		self.forCurve = forCurve

	def fwd(self,t):
		return self.spot * self.forCurve.df(t) / self.domCurve.df(t)

class ForwardCurveFromLinearPoints:
	def __init__(self,spot,t,points,fwdFactor=10000.):
		self.spot = spot
		self.t = t
		self.points = points,
		self.fwdFactor = 1./fwdFactor

		self.pointInterpolator = LinearInterpolator(np.concatenate([[0.],t]),
																								np.concatenate([[0.],points]))

	def fwd(self,t):
		return self.spot + self.fwdFactor * self.pointInterpolator(t)

class ForwardHelper:
	@classmethod
	def implyForeignCurve(cls,fwdCurve,domCurve):
		t = fwdCurve.t
		spot = fwdCurve.fwd(0)
		forDf = [fwdCurve.fwd(ti) / spot * domCurve.df(ti) for ti in t ] # F = S * DF_for / DF_dom  => DF_for = F/S * DF_dom
		zr = [-np.log(forDfi)/ti for ti,forDfi in zip(t,forDf)]
		return InterpolatedZeroCurve(LinearInterpolator(t,zr))

class FxMarket:
	def __init__(self,dfDomCurve,dfForCurve,fwdCurve):
		self.dfDomCurve = dfDomCurve
		self.dfForCurve = dfForCurve
		self.fwdCurve = fwdCurve

	def spot(self):
		return self.fwdCurve.fwd(0.) 

class HestonParams:
	def __init__(self,var0,kappa,theta,xi,rho):
		self.var0 = var0
		self.kappa = kappa
		self.theta = theta 
		self.xi = xi
		self.rho = rho


class HestonMarket(FxMarket):
	def __init__(self, dfDomCurve, dfForCurve, fwdCurve, hestonParams):
		super(HestonMarket).__init__(self,dfDomCurve,dfForCurve,fwdCurve)
		self.hestonParams = hestonParams


	def vanilla(self,ttm,strike):
		spot = self.spot()
		fwd = self.fwdCurve.fwd(ttm)
		params = heston.HestonParams(
			s0 = spot,
			v0 = self.hestonParams.var0,
			r = 0., # we compute undiscounted price, however fwd needs to match:
			q = np.log(spot/fwd)/ttm, # F = S*exp((r-q)*ttm) => q = r - ln(F/S) / ttm
			vMeanRevSpeed = self.hestonParams.kappa,
			vLongTermMean = self.hestonParams.theta,
			vVol = self.hestonParams.xi,
			svCorrelation = self.hestonParams.rho
		)
		model = heston.HestonLord(params)

		return self.dfDomCurve.df(ttm) * model.vanilla(strike,ttm)

	def impl_vol(self,ttm,strike):
		spot = self.spot()
		fwd = self.fwdCurve.fwd(ttm)
		params = heston.HestonParams(
			s0 = spot,
			v0 = self.hestonParams.var0,
			r = 0., # we compute undiscounted price, however fwd needs to match:
			q = np.log(spot/fwd)/ttm, # F = S*exp((r-q)*ttm) => q = r - ln(F/S) / ttm
			vMeanRevSpeed = self.hestonParams.kappa,
			vLongTermMean = self.hestonParams.theta,
			vVol = self.hestonParams.xi,
			svCorrelation = self.hestonParams.rho
		)
		model = heston.HestonLord(params)

		return model.smile(strike,ttm)		

class HestonCalibrator:
	def __init__(self, fxMarket):
		self.fxMarket = fxMarket

	def calibrate_to_single_smile(self,t,strikes,vols):
		obj = lambda params: sum((self.impl_vol(t,strikes,params)-vols)**2.)
		v = np.mean(vols)**2 * t
		iniParams = [v,1.,v,1.,0.]
		res = opt.minimize(obj,iniParam,method='nelder-mead')

	def impl_vol(self,t,strikes,params):
		hestonParams = HestonParams(*params)
		market = HestonMarket(self.fxMarket.dfDomCurve,self.fxMarket.dfForCurve,self.fxMarket.fwdCurve,hestonParams)
		return [market.impl_vol(t,k) for k in strikes]
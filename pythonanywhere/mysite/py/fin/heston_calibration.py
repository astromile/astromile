'''
    heston calibration
'''

import bisect

import numpy as np
import scipy.stats as st
import scipy.optimize as opt

import heston


class IRCurve:

    def df(self, t):
        raise NotImplementedError()


class ZeroCurve(IRCurve):

    def df(self, t):
        return np.exp(-t * self.zeroRate(t))

    def zeroRate(self, t):
        raise NotImplementedError()


class Interpolator:

    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)

    def locate(self, x):
        if x <= self.x[0]:
            return (0, 1)
        elif x >= self.x[-1]:
            n = len(self.x)
            return (n - 2, n - 1)
        else:
            left = bisect.bisect_left(self.x, x)
            return (left, left + 1)

    def __call__(self, x):
        raise NotImplementedError()


class InterpolatedZeroCurve(ZeroCurve):

    def __init__(self, interpolator):
        self.interpolator = interpolator

    def zeroRate(self, t):
        return self.interpolator(t)


class LinearInterpolator(Interpolator):

    def __init__(self, x, y):
        Interpolator.__init__(self, x, y)

        if len(x) > 1:
            self.dx = self.x[1:] - self.x[:-1]
            self.fx = (self.y[1:] - self.y[:-1]) / self.dx

    def __call__(self, x):
        if len(self.x) == 1:
            return self.y[0]
        elif len(self.x) > 1:
            left, _ = self.locate(x)
            return self.y[left] + self.fx[left] * (x - self.x[left]) / self.dx[left]


class ForwardCurve:

    def __init__(self, spot, domCurve, forCurve):
        self.spot = spot
        self.domCurve = domCurve
        self.forCurve = forCurve

    def fwd(self, t):
        return self.spot * self.forCurve.df(t) / self.domCurve.df(t)


class ForwardCurveFromLinearPoints:

    def __init__(self, spot, t, points, fwdFactor=10000.):
        self.spot = spot
        self.t = t
        self.points = points,
        self.fwdFactor = 1. / fwdFactor

        self.pointInterpolator = LinearInterpolator(np.concatenate([[0.], t]),
                                                    np.concatenate([[0.], points]))

    def fwd(self, t):
        return self.spot + self.fwdFactor * self.pointInterpolator(t)


class ForwardHelper:

    @classmethod
    def implyForeignCurve(cls, fwdCurve, domCurve):
        t = fwdCurve.t
        spot = fwdCurve.fwd(0)
        # F = S * DF_for / DF_dom  => DF_for = F/S * DF_dom
        forDf = [fwdCurve.fwd(ti) / spot * domCurve.df(ti) for ti in t]
        zr = [-np.log(dfi) / ti for ti, dfi in zip(t, forDf)]
        return InterpolatedZeroCurve(LinearInterpolator(t, zr))

    @classmethod
    def implyDomesticCurve(cls, fwdCurve, forCurve):
        t = fwdCurve.t
        spot = fwdCurve.fwd(0)
        # F = S * DF_for / DF_dom  => DF_dom = S/F * DF_for
        domDf = [spot / fwdCurve.fwd(ti) * forCurve.df(ti) for ti in t]
        zr = [-np.log(dfi) / ti for ti, dfi in zip(t, domDf)]
        return InterpolatedZeroCurve(LinearInterpolator(t, zr))


class FxMarket:

    def __init__(self, dfDomCurve, dfForCurve, fwdCurve):
        self.dfDomCurve = dfDomCurve
        self.dfForCurve = dfForCurve
        self.fwdCurve = fwdCurve

    def spot(self):
        return self.fwdCurve.fwd(0.)


class HestonParams:

    def __init__(self, var0, kappa, theta, xi, rho):
        self.var0 = var0
        self.kappa = kappa
        self.theta = theta
        self.xi = xi
        self.rho = rho

    def jsonify(self):
        # generally not a good idea
        # but it works in this particular case
        return self.__dict__


class HestonMarket(FxMarket):

    def __init__(self, dfDomCurve, dfForCurve, fwdCurve, hestonParams, hestonImpl=heston.HestonSingleIntegration):
        FxMarket.__init__(self, dfDomCurve, dfForCurve, fwdCurve)
        self.hestonParams = hestonParams
        self.hestonImpl = hestonImpl

    def vanilla(self, ttm, strike, callput):
        spot = self.spot()
        fwd = self.fwdCurve.fwd(ttm)
        params = heston.HestonParams(
            s0=spot,
            v0=self.hestonParams.var0,
            r=0.,  # we compute undiscounted price, however fwd needs to match:
            # F = S*exp((r-q)*ttm) => q = r - ln(F/S) / ttm
            q=np.log(spot / fwd) / ttm,
            vMeanRevSpeed=self.hestonParams.kappa,
            vLongTermMean=self.hestonParams.theta,
            vVol=self.hestonParams.xi,
            svCorrelation=self.hestonParams.rho
        )
        model = self.hestonImpl(params, integrationLimit=500.)

        return self.dfDomCurve.df(ttm) * model.vanilla(strike, ttm, callput)

    def impl_vol(self, ttm, strike):
        spot = self.spot()
        fwd = self.fwdCurve.fwd(ttm)
        params = heston.HestonParams(
            s0=spot,
            v0=self.hestonParams.var0,
            r=0.,  # we compute undiscounted price, however fwd needs to match:
            # F = S*exp((r-q)*ttm) => q = r - ln(F/S) / ttm
            q=np.log(spot / fwd) / ttm,
            vMeanRevSpeed=self.hestonParams.kappa,
            vLongTermMean=self.hestonParams.theta,
            vVol=self.hestonParams.xi,
            svCorrelation=self.hestonParams.rho
        )
        model = self.hestonImpl(params)

        return model.smile(strike, ttm)


class HestonCalibrator:

    def __init__(self, fxMarket):
        self.fxMarket = fxMarket

    def calibrate_to_single_smile(self, t, strikes, vols, iniParams):
        self.iniParams = iniParams

        def obj(params): return sum(
            (self.impl_vol(t, strikes, params) - vols) ** 2.)

        res = opt.minimize(obj, self.getIniParams(
            iniParams), method='nelder-mead')
        calibratedParams = self.getHestonParams(res.x)
        return calibratedParams

    def calibrate_to_surface(self, t, strikes, vols, iniParams, method, objective):
        self.iniParams = iniParams

        spot = self.fxMarket.spot()
        if objective == 'PV':
            otm_pvs = []
            for ti, ki, vi in zip(t, strikes, vols):
                fwd = self.fxMarket.fwdCurve.fwd(ti)
                r = -np.log(self.fxMarket.dfDomCurve.df(ti)) / ti
                q = -np.log(self.fxMarket.dfForCurve.df(ti)) / ti
                otm_pvs.append([heston.BS(heston.BSParams(spot, r, q, v)).vanilla(k, ti, np.sign(k - fwd))
                       for k, v in zip(ki, vi)])

            def obj(params): return sum([sum((self.pvs(ti, ki, params) - pvs) ** 2.)
                                         for ti, ki, vi, pvs in zip(t, strikes, vols, otm_pvs)])

        else:
            def obj(params): return sum([sum((self.impl_vol(ti, ki, params) - vi) ** 2.)
                                     for ti, ki, vi in zip(t, strikes, vols)])

        np.seterr(all='raise')
        res = opt.minimize(obj, self.getIniParams(iniParams), method=method)
        calibratedParams = self.getHestonParams(res.x)
        return calibratedParams, res.fun

    def calibrate_to_surface_mc(self, t, strikes, vols, iniParams, nGen=300):
        self.iniParams = iniParams

        def obj(params): return sum([sum((self.impl_vol(ti, ki, params) - vi) ** 2.)
                                     for ti, ki, vi in zip(t, strikes, vols)])

        optParams = p0 = self.getIniParams(iniParams)
        optObj = obj(optParams)
        M = .001
        for i in xrange(nGen):
            if i % 20 == 0:
                p0 = optParams
            p = p0 + M * np.random.randn(len(p0))
            o = obj(p)
            if o < optObj:
                optObj = o
                optParams = p

        calibratedParams = self.getHestonParams(optParams)
        return calibratedParams, optObj

    def impl_vol(self, t, strikes, params):
        market = HestonMarket(self.fxMarket.dfDomCurve,
                              self.fxMarket.dfForCurve,
                              self.fxMarket.fwdCurve,
                              self.getHestonParams(params))
        return np.array([market.impl_vol(t, k) for k in strikes])

    def pvs(self, t, strikes, params):
        market = HestonMarket(self.fxMarket.dfDomCurve,
                              self.fxMarket.dfForCurve,
                              self.fxMarket.fwdCurve,
                              self.getHestonParams(params))
        fwd = self.fxMarket.fwdCurve.fwd(t)
        return np.array([market.vanilla(t, k, np.sign(k - fwd)) for k in strikes])

    def getIniParams(self, params):
        iniParams = []
        if not params['var0']['fixed']:
            iniParams.append(np.log(params['var0']['value']))
        if not params['kappa']['fixed']:
            iniParams.append(np.log(params['kappa']['value']))
        if not params['theta']['fixed']:
            iniParams.append(np.log(params['theta']['value']))
        if not params['xi']['fixed']:
            iniParams.append(np.log(params['xi']['value']))
        if not params['rho']['fixed']:
            iniParams.append(np.arctanh(params['rho']['value']))
        return iniParams

    def getHestonParams(self, params):
        idx = 0
        if self.iniParams['var0']['fixed']:
            var0 = self.iniParams['var0']['value']
        else:
            var0 = np.exp(params[idx])
            idx += 1
        if self.iniParams['kappa']['fixed']:
            kappa = self.iniParams['kappa']['value']
        else:
            kappa = np.exp(params[idx])
            idx += 1
        if self.iniParams['theta']['fixed']:
            theta = self.iniParams['theta']['value']
        else:
            theta = np.exp(params[idx])
            idx += 1
        if self.iniParams['xi']['fixed']:
            xi = self.iniParams['xi']['value']
        else:
            xi = np.exp(params[idx])
            idx += 1
        if self.iniParams['rho']['fixed']:
            rho = self.iniParams['rho']['value']
        else:
            rho = np.tanh(params[idx])
            idx += 1
        hestonParams = HestonParams(
            var0,
            kappa,
            theta,
            xi,
            rho
        )
        return hestonParams


class DeltaType:
    Spot = 0.
    Forward = 1.


class PremiumType:
    Excluded = -1.
    Included = 1.


class QuoteHelper:

    def __init__(self, fxMarket, deltaType, premiumType):
        self.fxMarket = fxMarket
        self.deltaType = deltaType
        self.premiumType = premiumType

    def atmStrike(self, ttm, atmVol):
        fwd = self.fxMarket.fwdCurve.fwd(ttm)
        return fwd * np.exp(-self.premiumType * atmVol ** 2. * ttm / 2.)

    def strikeForDelta(self, ttm, delta, vol):
        fwd = self.fxMarket.fwdCurve.fwd(ttm)
        deltaFwd = delta if self.deltaType == DeltaType.Forward \
            else delta / self.fxMarket.dfForCurve.df(ttm)

        if self.premiumType == PremiumType.Excluded:
            std = vol * np.sqrt(ttm)
            q = st.norm.ppf(np.abs(deltaFwd))
            return fwd * np.exp(std * (std / 2. - np.sign(delta) * q))
        else:
            callput = np.sign(delta)

            def obj(k): return delta - self.deltaBS(callput, ttm, k, vol)

            strike = opt.newton(obj, self.atmStrike(ttm, vol))
            return strike

    def deltaBS(self, callput, ttm, strike, vol):
        deltaFactor = 1. if self.deltaType == DeltaType.Forward \
            else self.fxMarket.dfForCurve.df(ttm)

        fwd = self.fxMarket.fwdCurve.fwd(ttm)
        std = vol * np.sqrt(ttm)
        d = np.log(fwd / strike) / std + std / 2.
        if self.premiumType:
            d -= std
            deltaFactor *= strike / fwd

        return callput * deltaFactor * st.norm.cdf(callput * d)


def testAtmStructure():
    import matplotlib.pyplot as plt
    domCurve = InterpolatedZeroCurve(LinearInterpolator([1.], [0.]))
    forCurve = InterpolatedZeroCurve(LinearInterpolator([1.], [0.]))
    spot = 1.6235
    fwdCurve = ForwardCurve(spot, domCurve, forCurve)
    hParams = HestonParams(var0=0.01,
                           kappa=1.,
                           theta=0.01,
                           xi=1.,
                           rho=0.)
    t = np.concatenate([[1. / 252.], np.arange(1, 4) / 52.,
                        np.arange(1, 25) / 12., np.arange(3., 11.)])  # , [100.]])
    factors = {'var0':-.005, 'theta':-.005,
               'kappa':-0.5, 'xi': 0.8, 'rho':-0.9}
    param = 'kappa'
    for dx in np.linspace(-10., 1., 11):
        atmStrikes = []
        atmVols = []
        for ttm in t:
            fwd = fwdCurve.fwd(ttm)
            h1 = [getattr(hParams, p) + factors[p] * (dx if param == p else 0.)
                  for p in ['var0', 'kappa', 'theta', 'xi', 'rho']]
            h1 = HestonParams(*h1)
            m1 = HestonMarket(domCurve, forCurve, fwdCurve, h1)
            atmStrike = opt.newton(
                lambda k: k - fwd * np.exp(m1.impl_vol(ttm, k) ** 2. * ttm / 2.), fwd)
            atmStrikes.append(atmStrike)
            atmVols.append(m1.impl_vol(ttm, atmStrike))

        lbl = 'v_0' if param == 'var0' else '\\' + param
        lbl = '$' + lbl + \
            '={:.4f}$'.format(getattr(hParams, param) + dx * factors[param])
        plt.plot(t, atmVols, '-' if dx == 0. else '--', label=lbl)
        print 'plotted for dx =', dx

    plt.legend(loc='best')
    plt.title(
        r'$\sigma_I(T;v_0={0.var0:.4f}, \kappa={0.kappa:.2f}, \theta={0.theta:.4f}, \xi={0.xi:.2f}, \rho={0.rho:.2f})$'.format(hParams))
    plt.ylim(0., 0.15)
    plt.tight_layout()
    plt.show()


def testSmileStructures():
    import matplotlib.pyplot as plt
    domCurve = InterpolatedZeroCurve(LinearInterpolator([1.], [0.]))
    forCurve = InterpolatedZeroCurve(LinearInterpolator([1.], [0.]))
    spot = 1.6235
    fwdCurve = ForwardCurve(spot, domCurve, forCurve)
    hParams = HestonParams(var0=0.01,
                           kappa=1.,
                           theta=0.01,
                           xi=1.,
                           rho=0.)
    ttm = 10.
    factors = {'var0':-.005, 'theta':-.005,
               'kappa':-0.5, 'xi': 0.8, 'rho':-0.9}
    param = 'rho'
    strikes = np.linspace(1.5, 1.8)
    for dx in np.linspace(-1., 1., 11):
        vols = []
        for strike in strikes:
            h1 = [getattr(hParams, p) + factors[p] * (dx if param == p else 0.)
                  for p in ['var0', 'kappa', 'theta', 'xi', 'rho']]
            h1 = HestonParams(*h1)
            m1 = HestonMarket(domCurve, forCurve, fwdCurve, h1)
            vols.append(m1.impl_vol(ttm, strike))

        lbl = 'v_0' if param == 'var0' else '\\' + param
        lbl = '$' + lbl + \
            '={:.4f}$'.format(getattr(hParams, param) + dx * factors[param])
        plt.plot(strikes, vols, '-' if dx == 0. else '--', label=lbl)
        print 'plotted for dx =', dx

    plt.legend(loc='best')
    plt.title(
        r'$\sigma_I(K;T={1}, v_0={0.var0:.4f}, \kappa={0.kappa:.2f}, \theta={0.theta:.4f}, \xi={0.xi:.2f}, \rho={0.rho:.2f})$'.format(hParams, ttm))
    plt.ylim(0., 0.15)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':


    # testAtmStructure()
    testSmileStructures()


import numpy as np
import scipy.stats as st
import scipy.integrate as spi
from scipy.optimize.zeros import newton, brentq
import datetime


class BSParams:

    def __init__(self, s0, r, q, sVol):
        self.s0 = s0
        self.r = r
        self.q = q
        self.vol = sVol


class HestonParams:

    def __init__(self, s0, v0, r, q, vMeanRevSpeed, vLongTermMean, vVol, svCorrelation, priceOfVol=0.):
        self.s0 = s0
        self.v0 = v0
        self.r = r
        self.q = q
        self.kappa = vMeanRevSpeed
        self.theta = vLongTermMean
        self.xi = vVol
        self.rho = svCorrelation
        self.lmbda = priceOfVol

    def isFeller(self):
        return 2. * self.kappa * self.theta > self.xi ** 2

    def __str__(self):
        return 'Heston[{}]'.format(' '.join(map(lambda k: '{}={}'.format(k, getattr(self, k)),
                                                ['s0', 'v0', 'r', 'q', 'kappa', 'theta', 'xi', 'rho'])))

    def __repr__(self):
        return str(self)


class BS:

    def __init__(self, params):
        self.m = params

    def call(self, strike, ttm):
        P1, P2 = self.P12(np.log(strike), ttm)
        return self.m.s0 * np.exp(-self.m.q * ttm) * P1 \
            - strike * np.exp(-self.m.r * ttm) * P2

    def put(self, strike, ttm):
        return self.call(strike, ttm) \
            - self.m.s0 * np.exp(-self.m.q * ttm) \
            + strike * np.exp(-self.m.r * ttm)

    def vanilla(self, strike, ttm, phi):
        return self.call(strike, ttm) if phi == 1 else self.put(strike, ttm)

    def P12(self, k, ttm):
        std = self.m.vol * np.sqrt(ttm)
        fwd = self.m.s0 * np.exp((self.m.r - self.m.q) * ttm)
        k = np.log(fwd) - k
        errs = np.geterr()
        try:
            np.seterr(divide='raise', over='raise')
            d1 = k / std + std / 2.
            d2 = d1 - std
            return st.norm.cdf([d1, d2])
        except FloatingPointError:
            return np.ones(2) * np.sign(k)
        finally:
            np.seterr(divide=errs['divide'], over=errs['over'])

    def impliedVol(self, strike, ttm, pv, callput, guess=None):
        atm = self.m.vol if guess is None else guess

        def obj(sigma): return pv - BS(BSParams(self.m.s0,
                                                  self.m.r,
                                                  self.m.q,
                                                  sigma)).vanilla(strike, ttm, callput)

        # return newton(obj, atm)

        '''
            braketing for better Brent performance
        '''
        l = r = atm
        step = 1.05
        if obj(atm) > 0.:
            while True:
                r *= step
                if obj(r) < 0.:
                    break
                l = r / step
        else:
            while True:
                l /= step
                if obj(l) > 0.:
                    break
                r = l * step

        x = brentq(obj, l, r)
        return x

    def smile(self, strike, ttm):  # @UnusedVariable
        return self.m.vol


class Heston93:

    def __init__(self, params, integrationLimit=400.):
        self.m = params
        self.integrationLim = integrationLimit

    def smile(self, strike, ttm, guess=None):
        fwd = self.m.s0 * np.exp((self.m.r - self.m.q) * ttm)
        callput = 1. if strike > fwd else -1.
        hestonPv = self.vanilla(strike, ttm, callput)
        bs = BS(BSParams(self.m.s0,
                         self.m.r,
                         self.m.q,
                         np.sqrt(np.abs(self.m.v0))))
        return bs.impliedVol(strike, ttm, hestonPv, callput, guess)

    def call(self, strike, ttm):
        P1, P2 = self.P12(np.log(strike), ttm)
        return self.m.s0 * np.exp(-self.m.q * ttm) * P1 - strike * np.exp(-self.m.r * ttm) * P2

    def put(self, strike, ttm):
        return self.call(strike, ttm) \
            - self.m.s0 * np.exp(-self.m.q * ttm) \
            + strike * np.exp(-self.m.r * ttm)

    def vanilla(self, strike, ttm, phi):
        return self.call(strike, ttm) if phi == 1 else self.put(strike, ttm)

    def P12(self, k, ttm):
        return map(lambda I: 0.5 + I / np.pi, self.I12(k, ttm))

    def I12(self, k, ttm):
        I = []
        for j in [1, 2]:

            def integrand_j(w): return self.integrand(w, j, k, ttm)

            # res, _ = spi.quad(integrand_j, 0.0, np.inf)
            res, _ = spi.quad(integrand_j, 0.0, self.integrationLim)
            I.append(res)
            # assert err < 1.e-6

        return I

    def integrand(self, w, j, k, ttm):
        err = np.geterr()
        np.seterr(under='ignore')
        v = np.real(np.exp(-1j * w * k) * self.cf(j, ttm, w) / (1j * w))
        np.seterr(under=err['under'])
        return v

    def cf(self, j, ttm, w):
        m = self.m
        x = np.log(m.s0)
        a = m.kappa * m.theta
        b = m.kappa + m.lmbda - (m.rho * m.xi if j == 1 else 0.)
        u = 1.5 - j
        q = m.rho * m.xi * w * 1j
        d = np.sqrt((q - b) ** 2 - m.xi ** 2 * (2. * u * w * 1j - w ** 2))
        gp = b - q + d
        gm = b - q - d
        g = gp / gm

        C = (m.r - m.q) * w * 1j * ttm + a / m.xi ** 2 * (
            ttm * gp
            - 2 * np.log((1. - g * np.exp(d * ttm)) / (1. - g))
        )
        D = gp / m.xi ** 2 \
            * (np.exp(-d * ttm) - 1.) / (np.exp(-d * ttm) - g)

        return np.exp(C + D * m.v0 + 1j * w * x)


'''
    see, e.g. https://arxiv.org/pdf/1511.08718.pdf
'''
class HestonCommonCF(Heston93):

    def __init__(self, params, integrationLimit=np.inf):
        Heston93.__init__(self, params, integrationLimit=integrationLimit)

    def integrand(self, w, j, k, ttm):
        if j == 1:
            return np.real(np.exp(-1j * w * k) * self.cf_lnS(w - 1j, ttm)
                           / (1j * w * self.cf_lnS(-1j, ttm)))
        else:
            return np.real(np.exp(-1j * w * k) * self.cf_lnS(w, ttm) / (1j * w))

    def cf_lnS(self, w, ttm):
        m = self.m

        alpha = -w / 2. * (w + 1j)
        beta = m.kappa - m.rho * m.xi * w * 1j
        gamma = m.xi ** 2 / 2.

        h = np.sqrt(beta ** 2 - 4. * alpha * gamma)
        rp = (beta + h) / m.xi ** 2
        rm = (beta - h) / m.xi ** 2
        g = rm / rp

        under = np.geterr()['under']
        np.seterr(under='ignore')
        C = m.kappa * (rm * ttm - 2. / m.xi ** 2 *
                       np.log((1. - g * np.exp(-h * ttm)) / (1. - g)))
        D = rm * (1. - np.exp(-h * ttm)) / (1. - g * np.exp(-h * ttm))
        cf = np.exp(C * m.theta + D * m.v0 + 1j * w * (np.log(m.s0) + (m.r - m.q) * ttm))
        np.seterr(under=under)

        return cf

'''
    see http://www.rogerlord.com/complexlogarithmsheston.pdf
'''
class HestonLord(Heston93):

    def __init__(self, params, integrationLimit=np.inf):
        Heston93.__init__(self, params, integrationLimit=integrationLimit)

    def cf(self, j, ttm, w):
        m = self.m
        x = np.log(m.s0)
        a = m.kappa * m.theta
        b = m.kappa + m.lmbda - (m.rho * m.xi if j == 1 else 0.)
        u = 1.5 - j
        q = m.rho * m.xi * w * 1j
        d = np.sqrt((q - b) ** 2 - m.xi ** 2 * (2. * u * w * 1j - w ** 2))
        gp = b - q + d
        gm = b - q - d
        g = gp / gm

        under = np.geterr()['under']
        np.seterr(under='ignore')
        C = (m.r - m.q) * w * 1j * ttm + a / m.xi ** 2 * (
            ttm * gm
            - 2 * np.log((np.exp(-d * ttm) - g) / (1. - g))
        )
        D = gp / m.xi ** 2 \
            * (np.exp(-d * ttm) - 1.) / (np.exp(-d * ttm) - g)
        res = np.exp(C + D * m.v0 + 1j * w * x)
        np.seterr(under=under)

        return res


class HestonSingleIntegration(HestonLord):

    def __init__(self, params, integrationLimit=np.inf, integrationScheme='quad'):
        HestonLord.__init__(self, params, integrationLimit=integrationLimit)
        self.integrationScheme = integrationScheme

    def call(self, strike, ttm):
        k = np.log(strike)
        a1 = self.m.s0 * np.exp(-self.m.q * ttm)
        a2 = strike * np.exp(-self.m.r * ttm)

        err = np.geterr()
        np.seterr(under='ignore')

        def integrand(w):
            i1 = self.integrand(w, 1, k, ttm)
            i2 = self.integrand(w, 2, k, ttm)
            return (a1 * i1 - a2 * i2) / np.pi


        if self.integrationScheme == 'quad':
            I = self.integrate_quad(integrand)
        elif self.integrationScheme == 'fixed_quad':
            I = self.integrate_fixed_quad(integrand)
        elif self.integrationScheme == 'romb':
            I = self.integrate_romb1(integrand)
        elif self.integrationScheme == 'romberg':
            I = self.integrate_romberg(integrand)
        elif self.integrationScheme == 'quadromb':
            I = self.integrate_romb2(integrand)
        else:
            raise ValueError('Unsupported integration scheme {}'.format(self.integrationScheme))

        np.seterr(under=err['under'])

        return (a1 - a2) / 2. + I

    def integrate_quad(self, integrand):
        # subdivide for better performance
        b = 100.
        pv1, _ = spi.quad(integrand, 0., b)
        pv2, _ = spi.quad(integrand, b, self.integrationLim)
        return pv1 + pv2

    def integrate_fixed_quad(self, integrand):
        # subdivide for better performance
        b = 100.
        pv1, _ = spi.fixed_quad(integrand, 1.e-9, 500., n=200)
        return pv1

    def integrate_romberg(self, integrand):
        # subdivide for better performance
        b = 100.
        pv1 = spi.romberg(integrand, 1.e-9, b)
        pv2 = spi.romberg(integrand, b, min(self.integrationLim, 700.))
        return pv1 + pv2

    def integrate_romb(self, integrand):
        # subdivide for better performance
        a = 1.e-9
        b = 20.
        c = self.integrationLim if self.integrationLim < np.inf else 400.

        n1 = 2 ** 8 + 1
        n2 = 2 ** 9 + 1

        pv = spi.romb(integrand(np.linspace(a, b, n1)),
                       (b - a) / (n1 - 1))
        pv += spi.romb(integrand(np.linspace(b, c, n2)),
                       (c - b) / (n2 - 1))

        if self.integrationLim == np.inf:
            pvinf, _ = spi.quad(integrand, c, np.inf)
            pv += pvinf

        return pv

    def integrate_romb1(self, integrand):
        # subdivide for better performance
        a = [1.e-9, 1., 5., 20.] + ([self.integrationLim] if self.integrationLim < np.inf else [400., np.inf])
        k = [4, 5, 6, 9]
        if self.m.xi > 1.:
            k[0] += 2
        pv = 0.
        for i in xrange(len(a) - 1):
            l = a[i]
            r = a[i + 1]
            if r == np.inf:
                pvi, _ = spi.quad(integrand, l, r)
                pv += pvi
            else:
                x = np.linspace(l, r, 2 ** k[i] + 1).reshape((1, -1))
                pv += spi.romb(integrand(x),
                               (r - l) / 2 ** k[i])

        return pv.reshape((-1, 1))

    def integrate_romb2(self, integrand):
        # subdivide for better performance
        a = [0., 1., 5., 20.] + ([self.integrationLim] if self.integrationLim < np.inf else [400., np.inf])
        k = [4, 5, 6, 9]
        if self.m.xi > 1.:
            k[0] += 2
        pv = 0.
        for i in xrange(len(a) - 1):
            l = a[i]
            r = a[i + 1]
            if l == 0. or r == np.inf:
                pvi, _ = spi.quad(integrand, l, r)
                pv += pvi
            else:
                pv += spi.romb(integrand(np.linspace(l, r, 2 ** k[i] + 1)),
                               (r - l) / 2 ** k[i])

        return pv


class PremiumType:
    Included = 1
    Excluded = 0


class DeltaType:
    Spot = 1
    Forward = 0


class DeltaHelper:

    def __init__(self, model):
        self.m = model

    def deltaBS(self, strike, ttm, callput=1., premiumType=PremiumType.Excluded, deltaType=None):
        if deltaType is None:
            deltaType = DeltaType.Spot if ttm < 1. else DeltaType.Forward

        volImpl = self.m.smile(strike, ttm)

        fwd = self.m.m.s0 * np.exp((self.m.m.r - self.m.m.q) * ttm)
        std = volImpl * np.sqrt(ttm)
        d = np.log(fwd / strike) / std + std / 2.
        dsc = 1.
        if premiumType == PremiumType.Included:
            d -= std
            dsc *= strike / fwd

        if deltaType == DeltaType.Spot:
            dsc *= np.exp(-self.m.m.q * ttm)

        return callput * dsc * st.norm.cdf(callput * d)

    def atmStrike(self, ttm, premiumType=PremiumType.Excluded, deltaType=DeltaType.Spot):
        fwd = self.m.m.s0 * np.exp((self.m.m.r - self.m.m.q) * ttm)

        atmVol = self.m.smile(fwd, ttm)
        strike = fwd * np.exp((0.5 if premiumType ==
                               PremiumType.Excluded else -0.5) * atmVol ** 2 * ttm)

        def obj(k): return self.deltaBS(k, ttm, 1., premiumType, deltaType) \
            + self.deltaBS(k, ttm, -1., premiumType, deltaType)

        strike = newton(obj, strike)
        return strike

    def atmVol(self, ttm, premiumType=PremiumType.Excluded, deltaType=DeltaType.Spot):
        atmStrike = self.atmStrike(ttm, premiumType, deltaType)
        atmVol = self.m.smile(atmStrike, ttm)
        return atmVol

    def volForDelta(self, delta, ttm, premiumType=PremiumType.Excluded, deltaType=DeltaType.Spot):
        strike = self.strikeForDelta(delta, ttm, premiumType, deltaType)
        vol = self.m.smile(strike, ttm)
        return vol

    def strikeForDelta(self, delta, ttm, premiumType=PremiumType.Excluded, deltaType=DeltaType.Spot):
        strike = self.m.m.s0 * np.exp((self.m.m.r - self.m.m.q) * ttm)
        callput = 1. if delta > 0. else -1.

        def obj(k): return self.deltaBS(
            k, ttm, callput, premiumType, deltaType) - delta

        strike = newton(obj, strike)
        return strike



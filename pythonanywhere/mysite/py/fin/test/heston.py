'''
Created on Nov 27, 2017

@author: Alexander
'''
import unittest
from fin.heston import HestonParams, HestonSingleIntegration, Heston93, \
    HestonCommonCF, HestonLord, BSParams, BS

import numpy as np
import datetime

class Test(unittest.TestCase):
    TEST_EXACT = False
    PRECISION = 15

    def testRegression(self):
        regression = [
            (HestonParams(s0=1.,
                         v0=0.01,
                         r=0., q=0.,
                         vMeanRevSpeed=1.,
                         vLongTermMean=0.01,
                         vVol=1.,
                         svCorrelation=0.),
                 1., 1.,
                 0.022501121622415604),
            (HestonParams(s0=1.,
                         v0=0.01,
                         r=0., q=0.,
                         vMeanRevSpeed=1.,
                         vLongTermMean=0.01,
                         vVol=1.,
                         svCorrelation=0.2),
                 1., 1.,
                 0.022579055466660142),
            (HestonParams(s0=1.,
                         v0=0.16,
                         r=0., q=0.,
                         vMeanRevSpeed=1.,
                         vLongTermMean=0.16,
                         vVol=2.,
                         svCorrelation=-0.8),
                 2., 10.,
                 0.049521147208797744),
            (HestonParams(s0=100.,
                         v0=0.04,
                         r=0.02, q=0.,
                         vMeanRevSpeed=1.5,
                         vLongTermMean=0.06,
                         vVol=0.7,
                         svCorrelation=0.8),
                 110., 0.25,
                 1.680798168853325336),
            ]

        for p, k, t, v in  regression:
            v1 = HestonSingleIntegration(p,
                                         integrationLimit=np.inf,
                                         integrationScheme='quad').call(k, t)
            
            self.assertRegression(v1, v,
                                  'Call(k={k}, t={t}; {p}) = {v1:.18f} <> {v:.18f} [{diff}]'
                                  .format(k=k, t=t, p=p, v=v, v1=v1, diff=v1 - v))


    def assertRegression(self, xactual, xexpected, msg, precision=None):
        if self.TEST_EXACT:
            self.assertEquals(xactual, xexpected, msg)
        else:
            self.assertAlmostEqual(xactual, xexpected,
                                   places=self.PRECISION if precision is None else precision,
                                   msg=msg)

    def testIsometry(self):
        spot = 1.6235
        v0 = 0.001
        r = 0.025
        q = 0.04

        kappa = 0.5
        theta = 0.001
        xi = 0.1
        rho = -0.2

        t = 1.
        dfCHF = np.exp(-r * t)
        dfEUR = np.exp(-q * t)
        fwd = spot * dfEUR / dfCHF

        # test isometries
        p1 = HestonParams(s0=spot,
                          v0=v0,
                          r=r,
                          q=q,
                          vMeanRevSpeed=kappa,
                          vLongTermMean=theta,
                          vVol=xi,
                          svCorrelation=rho)

        p2 = HestonParams(s0=fwd,
                          v0=v0,
                          r=0,
                          q=0,
                          vMeanRevSpeed=kappa,
                          vLongTermMean=theta,
                          vVol=xi,
                          svCorrelation=rho)

        pricer1 = HestonSingleIntegration(p1)
        pricer2 = HestonSingleIntegration(p2)

        strikes = np.linspace(1.5, 1.7)

        for strike in strikes:
            pvtrue = pricer1.put(strike, t)
            pvscaled = pricer2.put(strike, t) * dfCHF
            self.assertAlmostEqual(pvtrue, pvscaled, places=15,
                             msg='isometry failed, eps={}'.format(abs(pvtrue - pvscaled)))


    def testConvergence2BS(self):
        vol = 0.1
        hp = HestonParams(s0=1.,
                          v0=vol ** 2.,
                          r=0., q=0.,
                          vMeanRevSpeed=1.,
                          vLongTermMean=vol ** 2.,
                          vVol=5.e-6,
                          svCorrelation=-0.8)
        bsp = BSParams(s0=hp.s0, r=hp.r, q=hp.q, sVol=vol)
        strike = 2.
        ttm = 10.
        pv_bs = BS(bsp).call(strike, ttm)
        pv_h = HestonSingleIntegration(hp).call(strike, ttm)

        self.assertAlmostEquals(pv_bs, pv_h, 7)

    def testImpliedVolComputation(self):
        spot = 1.6235
        v0 = 0.001
        r = 0.025
        q = 0.04

        kappa = 0.5
        theta = 0.001
        xi = 0.1
        rho = -0.2

        t = 1.
        dfCHF = np.exp(-r * t)
        dfEUR = np.exp(-q * t)
        fwd = spot * dfEUR / dfCHF

        # test isometries
        p1 = HestonParams(s0=spot,
                          v0=v0,
                          r=r,
                          q=q,
                          vMeanRevSpeed=kappa,
                          vLongTermMean=theta,
                          vVol=xi,
                          svCorrelation=rho)

        pricer = HestonSingleIntegration(p1, np.inf, 'quad')
        lm = np.linspace(-0.1, 0.1)
        smile = []
        impl_vol = []
        for lmi in lm:
            strike = fwd * np.exp(lmi)
            smile.append(pricer.smile(strike, t))
            impl_vol.append(pricer.impl_vol(strike, t))
            print lmi, smile[-1], impl_vol[-1]
        import matplotlib.pyplot as plt
        plt.plot(lm, smile, label='smile')
        plt.plot(lm, impl_vol, label='impl_vol')
        plt.legend(loc='best')
        plt.show()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRegression']
    unittest.main()

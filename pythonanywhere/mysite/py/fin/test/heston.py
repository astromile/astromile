'''
Created on Nov 27, 2017

@author: Alexander
'''
import unittest
from fin.heston import HestonParams, HestonSingleIntegration, Heston93, \
    HestonCommonCF, HestonLord

import numpy as np

class Test(unittest.TestCase):
    TEST_EXACT = True
    PRECISION = 10

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
                                         integrationScheme='romberg').call(k, t)
            
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



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRegression']
    unittest.main()

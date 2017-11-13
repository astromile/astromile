from fin.heston import Heston93
from fin.heston_calibration import *

import numpy as np
from datetime import datetime


def tenor2ttm(tenor):
    m = {'ON': 1. / 252,
         '1W': 1. / 52,
         '2W': 2. / 52,
         '3W': 3. / 52,
         '1M': 1. / 12,
         '2M': 2. / 12,
         '3M': 3. / 12,
         '4M': 4. / 12,
         '5M': 5. / 12,
         '6M': 6. / 12,
         '7M': 7. / 12,
         '8M': 8. / 12,
         '9M': 9. / 12,
         '10M': 10. / 12,
         '11M': 11. / 12,
         '12M': 1.,
         '1Y': 1.,
         '2Y': 2.,
         '3Y': 3.,
         '4Y': 4.,
         '5Y': 5.
         }

    return m[tenor]


def calibrateToSingleSmile():
    spot = 1.6235
    ttm = 1.
    input_quotes = [{
        'tenor': '1Y',
        'df':0.975420395,
        'fwd':-254.36,
        'rr25':-0.00350,
        'atm':.02975,
        'bf25':0.00150
        }]

    t = []
    zrDom = []
    fwdPoints = []
    vols = []
    for q in input_quotes:
        t.append(tenor2ttm(q['tenor']))
        zrDom.append(-np.log(q['df']) / t[-1])
        fwdPoints.append(q['fwd'])
        atm = q['atm']
        rr = q['rr25']
        bf = q['bf25']
        vols.append([atm + bf - rr / 2., atm, atm + bf + rr / 2.])

    domCurve = InterpolatedZeroCurve(LinearInterpolator(t, zrDom))
    fwdPointsCurve = ForwardCurveFromLinearPoints(spot, t, fwdPoints)
    forCurve = ForwardHelper.implyForeignCurve(fwdPointsCurve, domCurve)
    fwdCurve = ForwardCurve(spot, domCurve, forCurve)
    fxMkt = FxMarket(domCurve, forCurve, fwdCurve)

    strikes = []
    premiumType = PremiumType.Excluded
    for ti, smile in zip(t, vols):
        deltaType = DeltaType.Spot if ti < 1. else DeltaType.Forward
        quoteHelper = QuoteHelper(fxMkt, deltaType, premiumType)
        strikes.append([quoteHelper.strikeForDelta(ti, -0.25, smile[0]),
                        quoteHelper.atmStrike(ti, smile[1]),
                        quoteHelper.strikeForDelta(ti, 0.25, smile[2])])

    calibrator = HestonCalibrator(fxMkt)

    iniParams = {'var0':{'value':0.001, 'fixed':False},
                 'theta':{'value':0.001, 'fixed':False},
                 'kappa':{'value':1., 'fixed':True},
                 'xi':{'value':0.1, 'fixed':False},
                 'rho':{'value':-0.2, 'fixed':False}}

    tStart = datetime.now()
    optParams, err = calibrator.calibrate_to_surface(t,
                                    strikes,
                                    vols,
                                    iniParams,
                                    method='Nelder-Mead')
    tEnd = datetime.now()
    print 'calibration finished in', tEnd - tStart
    print 'error', err
    print optParams.jsonify()


if __name__ == '__main__':
    import cProfile
    cProfile.run('calibrateToSingleSmile()', sort=1)

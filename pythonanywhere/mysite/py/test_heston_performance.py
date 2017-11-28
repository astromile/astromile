
from datetime import datetime
import numpy as np
from fin.heston_calibration import *

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
    input_quotes = [{
        'tenor': '1Y',
        'df':0.975420395,
        'fwd':-254.36,
        'rr25':-0.00350,
        'rr10':-0.00630,
        'atm':.02975,
        'bf25':0.00150,
        'bf10':0.00525
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
        rr25 = q['rr25']
        bf25 = q['bf25']
        rr10 = q['rr10']
        bf10 = q['bf10']
        vols.append([atm + bf10 - rr10 / 2.,
                     atm + bf25 - rr25 / 2.,
                     atm,
                     atm + bf25 + rr25 / 2.,
                     atm + bf10 + rr10 / 2.])

    domCurve = InterpolatedZeroCurve(LinearInterpolator(t, zrDom))
    fwdPointsCurve = ForwardCurveFromLinearPoints(spot, t, fwdPoints)
    forCurve = ForwardHelper.implyForeignCurve(fwdPointsCurve, domCurve)
    fwdCurve = ForwardCurve(spot, domCurve, forCurve)
    fxMkt = FxMarket(domCurve, forCurve, fwdCurve)

    strikes = []
    premiumType = PremiumType.Included
    for ti, smile in zip(t, vols):
        deltaType = DeltaType.Spot if ti <= 1. else DeltaType.Forward
        quoteHelper = QuoteHelper(fxMkt, deltaType, premiumType)
        strikes.append([quoteHelper.strikeForDelta(ti, -0.10, smile[0]),
                        quoteHelper.strikeForDelta(ti, -0.25, smile[1]),
                        quoteHelper.atmStrike(ti, smile[2]),
                        quoteHelper.strikeForDelta(ti, 0.25, smile[3]),
                        quoteHelper.strikeForDelta(ti, 0.10, smile[4])
                        ])

    calibrator = HestonCalibrator(fxMkt)

    iniParams = {'var0':{'value':0.001314063, 'fixed':False},
                 'theta':{'value':0.000849723, 'fixed':False},
                 'kappa':{'value':0.6666667, 'fixed':True},
                 'xi':{'value':0.033659521, 'fixed':False},
                 'rho':{'value':-0.117647059, 'fixed':False}}

    tStart = datetime.now()
    optParams, err = calibrator.calibrate_to_surface(t,
                                    strikes,
                                    vols,
                                    iniParams,
                                    method='Nelder-Mead',
                                    objective='PV')
    tEnd = datetime.now()
    print 'calibration finished in', tEnd - tStart
    print 'error', err
    print optParams.jsonify()


if __name__ == '__main__':
    import cProfile
    cProfile.run('calibrateToSingleSmile()', sort=1)

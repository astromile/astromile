# Flask app for pricing Vanillas in 'classical' models, e.g., BS, Heston, etc.

from flask import Flask, render_template, request, json
from flask_cors import CORS

import datetime as dt
import scipy.stats as st
import numpy as np

import matplotlib.pyplot as plt
import mpld3

from fin.heston import HestonLord, HestonParams
import fin.heston_calibration as hcal

app = Flask(__name__)

# ## this is a dev hack to test with "npm run dev" the client (js) side
MY_CORS = CORS(app, origins=['http://localhost:8080'])

''' classical BS '''


def bs_pv(spot, vol, r, q, strike, ttm, phi):
    fwd = spot * np.exp((r - q) * ttm)
    df = np.exp(-r * ttm)

    std = vol * np.sqrt(ttm)
    dp = np.log(fwd / strike) / std + std / 2.
    dm = dp - std

    return df * phi * (fwd * st.norm.cdf(phi * dp) - strike * st.norm.cdf(phi * dm))


''' heston analytical pricer based on CF integration '''


def heston_pv(spot, var0, r, q, kappa, theta, xi, rho, strike, ttm, phi):
    params = HestonParams(spot, var0, r, q, kappa, theta, xi, rho)
    model = HestonLord(params)

    return model.vanilla(strike, ttm, phi)


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


def heston_calibrate_to_single_smile(spot, input_quotes, ini_params, method, premiumType, objective):
    tStartMethod = dt.datetime.now()
    t = []
    zrDom = []
    fwdPoints = []
    smiles = []
    tenors = []
    deltaTypes = []

    for q in input_quotes:
        tenors.append(q['tenor'])
        ttm = tenor2ttm(tenors[-1])
        df = float(q['df'])
        fwd = float(q['fwd'])
        rr25 = float(q['rr25']) / 100.
        atm = float(q['atm']) / 100.
        bf25 = float(q['bf25']) / 100.
        if 'rr10' in q:
            rr10 = float(q['rr10']) / 100.
            bf10 = float(q['bf10']) / 100.

        deltaTypes.append(hcal.DeltaType.Spot if q['deltaType'] == 'Spot' else hcal.DeltaType.Forward)

        t.append(ttm)
        zrDom.append(-np.log(df) / ttm)
        fwdPoints.append(fwd)
        if 'rr10' in q:
            smiles.append([atm + bf10 - rr10 / 2.,
                           atm + bf25 - rr25 / 2.,
                           atm,
                           atm + bf25 + rr25 / 2.,
                           atm + bf10 + rr10 / 2.])
        else:
            smiles.append([atm + bf25 - rr25 / 2.,
                           atm,
                           atm + bf25 + rr25 / 2.])

    fwdPointsCurve = hcal.ForwardCurveFromLinearPoints(spot, t, fwdPoints)
    dfDomCurve = hcal.InterpolatedZeroCurve(hcal.LinearInterpolator(t, zrDom))
    dfForCurve = hcal.ForwardHelper.implyForeignCurve(
        fwdPointsCurve, dfDomCurve)
    fwdCurve = hcal.ForwardCurve(spot, dfDomCurve, dfForCurve)
    fxMarket = hcal.FxMarket(dfDomCurve, dfForCurve, fwdCurve)

    premiumType = hcal.PremiumType.Included if premiumType == 'Included' else hcal.PremiumType.Excluded
    strikes = []
    for i in xrange(len(t)):
        quoteHelper = hcal.QuoteHelper(fxMarket,
                                       deltaTypes[i],
                                       premiumType)
        if 'rr10' in q:
            strikes.append([quoteHelper.strikeForDelta(t[i], -0.1, smiles[i][0]),
                            quoteHelper.strikeForDelta(t[i], -0.25, smiles[i][1]),
                            quoteHelper.atmStrike(t[i], smiles[i][2]),
                            quoteHelper.strikeForDelta(t[i], 0.25, smiles[i][3]),
                            quoteHelper.strikeForDelta(t[i], 0.1, smiles[i][4])])
        else:
            strikes.append([quoteHelper.strikeForDelta(t[i], -0.25, smiles[i][0]),
                            quoteHelper.atmStrike(t[i], smiles[i][1]),
                            quoteHelper.strikeForDelta(t[i], 0.25, smiles[i][-1])])

    # hParams = calibrator.calibrate_to_single_smile(
    #    ttm, strikes[0], smiles[0], ini_params)

    calibrator = hcal.HestonCalibrator(fxMarket)
    tStart = dt.datetime.now()
    if method == 'MC':
        hParams, optValue = calibrator.calibrate_to_surface_mc(t, strikes, smiles, ini_params)
    else:
        hParams, optValue = calibrator.calibrate_to_surface(t, strikes, smiles, ini_params, method, objective)
    tEnd = dt.datetime.now()

    result = {
        'hestonParams': hParams,
        'objectiveValue': optValue,
        'elapsedCalibration': str(tEnd - tStart),
        'elapsedTime': str(dt.datetime.now() - tStartMethod)}
    return result


def heston_plot(spot, input_quotes, premiumType, hestonParams, xaxis, yaxis, optValue):
    t = []
    zrDom = []
    fwdPoints = []
    smiles = []
    tenors = []
    deltaTypes = []

    for q in input_quotes:
        tenors.append(q['tenor'])
        ttm = tenor2ttm(tenors[-1])
        df = float(q['df'])
        fwd = float(q['fwd'])
        rr25 = float(q['rr25']) / 100.
        atm = float(q['atm']) / 100.
        bf25 = float(q['bf25']) / 100.
        if 'rr10' in q:
            rr10 = float(q['rr10']) / 100.
            bf10 = float(q['bf10']) / 100.

        deltaTypes.append(hcal.DeltaType.Spot if q['deltaType'] == 'Spot' else hcal.DeltaType.Forward)

        t.append(ttm)
        zrDom.append(-np.log(df) / ttm)
        fwdPoints.append(fwd)
        if 'rr10' in q:
            smiles.append([atm + bf10 - rr10 / 2.,
                           atm + bf25 - rr25 / 2.,
                           atm,
                           atm + bf25 + rr25 / 2.,
                           atm + bf10 + rr10 / 2.])
        else:
            smiles.append([atm + bf25 - rr25 / 2.,
                           atm,
                           atm + bf25 + rr25 / 2.])

    fwdPointsCurve = hcal.ForwardCurveFromLinearPoints(spot, t, fwdPoints)
    dfDomCurve = hcal.InterpolatedZeroCurve(hcal.LinearInterpolator(t, zrDom))
    dfForCurve = hcal.ForwardHelper.implyForeignCurve(
        fwdPointsCurve, dfDomCurve)
    fwdCurve = hcal.ForwardCurve(spot, dfDomCurve, dfForCurve)
    fxMarket = hcal.FxMarket(dfDomCurve, dfForCurve, fwdCurve)

    premiumType = hcal.PremiumType.Included if premiumType == 'Included' else hcal.PremiumType.Excluded
    strikes = []
    for i in xrange(len(t)):
        quoteHelper = hcal.QuoteHelper(fxMarket,
                                       deltaTypes[i],
                                       premiumType)
        if 'rr10' in q:
            strikes.append([quoteHelper.strikeForDelta(t[i], -0.1, smiles[i][0]),
                            quoteHelper.strikeForDelta(t[i], -0.25, smiles[i][1]),
                            quoteHelper.atmStrike(t[i], smiles[i][2]),
                            quoteHelper.strikeForDelta(t[i], 0.25, smiles[i][3]),
                            quoteHelper.strikeForDelta(t[i], 0.1, smiles[i][4])])
        else:
            strikes.append([quoteHelper.strikeForDelta(t[i], -0.25, smiles[i][0]),
                            quoteHelper.atmStrike(t[i], smiles[i][1]),
                            quoteHelper.strikeForDelta(t[i], 0.25, smiles[i][-1])])

    hParams = hcal.HestonParams(**hestonParams)
    hestonMarket = hcal.HestonMarket(dfDomCurve, dfForCurve, fwdCurve, hParams)

    figure, _ = plt.subplots()

    for i in xrange(len(t)):
        fwdi = fwdCurve.fwd(t[i])
        xPillars = kPillars = np.array(strikes[i])
        yPillars = np.array(smiles[i])
        k = np.linspace(0.9 * strikes[i][0], 1.1 * strikes[i][-1])
        k = np.array(sorted(set(k).union(kPillars)))
        x = k
        y = np.array([hestonMarket.impl_vol(t[i], xi) for xi in x])
        if xaxis == 'Log-Moneyness':
            x = np.log(k / fwdi)
            xPillars = np.log(xPillars / fwdi)
        elif xaxis == 'Delta':
            # - fwd unadj put delta is used here
            std = y * np.sqrt(t[i])
            x = st.norm.cdf(np.log(x / fwdi) / std - std / 2.)
            stdPillars = yPillars * np.sqrt(t[i])
            xPillars = st.norm.cdf(np.log(xPillars / fwdi) / stdPillars - stdPillars / 2.)
        elif xaxis == 'Strike':
            pass
        else:
            raise RuntimeError('Unsupported x-axis {}'.format(xaxis))

        if yaxis == 'Total Var.':
            y *= y * t[i]
            yPillars *= yPillars * t[i]
        elif yaxis == 'Volatility':
            pass
        elif yaxis == 'PV':
            y = [hestonMarket.vanilla(t[i], ki, np.sign(ki - fwdi)) for ki in k]
            yPillars = [hestonMarket.vanilla(t[i], ki, np.sign(ki - fwdi)) for ki in kPillars]
        elif yaxis == 'Density':
            pass
        else:
            raise RuntimeError('Unsupported y-axis {}'.format(yaxis))

        l = plt.plot(x, y, '--', label=tenors[i])
        color = l[0].get_color()

        plt.plot(xPillars, yPillars, 'o', color=color)

    plt.legend(loc='best')
    plt.title('Objective: {}'.format(float(optValue)))

    plotData = mpld3.fig_to_dict(figure)
    plt.close()

    result = {
        'plotData': plotData
        }
    return result


@app.route('/', methods=['GET'])
def main_page():
    try:
        links = [
            {
                'title': 'Black-Scholes Vanilla Pricer',
                'link': '/bs'
            },
            {
                'title': 'Heston Vanilla Pricer',
                'link': '/heston'
            },
            {
                'title': 'Heston Calibration to FX Surface',
                'link': '/heston/calibration'
            }
        ]
        return render_template('index.html', links=links)
    except Exception as e:
        return error_response(e)


def error_response(e):
    import sys
    import os
    etype, e, exc_tb = sys.exc_info()
    traceback = []
    while exc_tb is not None:
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        funcname = exc_tb.tb_frame.f_code.co_name
        line = exc_tb.tb_lineno
        traceback.append('{funcname}@{filename}:{line}'.format(filename=filename,
                                                               funcname=funcname,
                                                               line=line))
        exc_tb = exc_tb.tb_next

    src = '\n'.join(['<-- ' + tb for tb in traceback[::-1]])
    return json.dumps({'error': {
        'type': str(etype),
        'str': str(e),
        'repr': repr(e),
        'msg': e.message,
        'src': src}})


class JsonifiableEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'jsonify'):
            return obj.jsonify()
        return json.JSONEncoder.default(self, obj)


@app.route('/bs', methods=['GET'])
def bs_render():
    try:
        return render_template('vanilla_anal.html', MODEL='Black-Scholes')
    except Exception as e:
        return error_response(e)


@app.route('/heston')  # ,methods=['GET'])
def heston_render():
    try:
        return render_template('vanilla_anal.html', MODEL="Heston")
    except Exception as e:
        return error_response(e)


@app.route('/heston/calibration')
def heston_calibration_render():
    try:
        return render_template('model_calibration.html', MODEL='Heston')
    except Exception as e:
        return error_response(e)


@app.route('/heston/calibrate', methods=['GET'])
def heston_calibrate():
    try:
        spot = float(request.args['spot'])
        input_quotes = json.loads(request.args['input_quotes'])
        ini_params = json.loads(request.args['ini_params'])
        method = request.args['method']
        premium_type = request.args['premium_type']
        objective = request.args['objective']

        result = heston_calibrate_to_single_smile(
            spot, input_quotes, ini_params, method, premium_type, objective)

        return json.dumps(result, cls=JsonifiableEncoder)
    except Exception as e:
        return error_response(e)


@app.route('/heston/plot', methods=['GET'])
def heston_plot_request():
    try:
        spot = float(request.args['spot'])
        input_quotes = json.loads(request.args['input_quotes'])
        heston_params = json.loads(request.args['heston_params'])
        premium_type = request.args['premium_type']
        objective_value = request.args['objective_value']
        xaxis = request.args['xaxis']
        yaxis = request.args['yaxis']

        result = heston_plot(
            spot, input_quotes, premium_type, heston_params, xaxis, yaxis, objective_value)

        return json.dumps(result, cls=JsonifiableEncoder)
    except Exception as e:
        return error_response(e)


@app.route('/bs/price_anal', methods=['GET'])
def bs_price_anal():
    try:
        spot = float(request.args['spot'])
        vol = float(request.args['vol'])
        r = float(request.args['ir'])
        q = float(request.args['dy'])
        strike = float(request.args['strike'])
        ttm = float(request.args['ttm'])

        spotAnnualRange = spot * np.exp(vol * st.norm.ppf([0.005, 0.995]))
        call = bs_pv(spot, vol, r, q, strike, ttm, 1.)
        put = bs_pv(spot, vol, r, q, strike, ttm, -1.)

        result = {
            'spot_annual_range_99': list(spotAnnualRange),
            'pv_call': call,
            'pv_put': put
        }
        return json.dumps(result)
    except Exception as e:
        return error_response(e)


@app.route('/bs/plot_data', methods=['GET'])
def bs_plot_data():
    try:
        spot = float(request.args['spot'])
        vol = float(request.args['vol'])
        r = float(request.args['ir'])
        q = float(request.args['dy'])
        strike = float(request.args['strike'])
        ttm = float(request.args['ttm'])

        xaxis = request.args['xaxis']
        if xaxis in ['spot', 'vol', 'strike']:
            xrng = [0.7, 1.5] * np.ones(2) * float(request.args[xaxis])
        elif xaxis in ['ir', 'dy']:
            xrng = [-0.03, +0.03] * np.ones(2) + float(request.args[xaxis])
        elif xaxis == 'ttm':
            xrng = [0.1, 10.]

        xrng = np.linspace(xrng[0], xrng[1])
        ycall = [bs_pv(x if xaxis == 'spot' else spot,
                       x if xaxis == 'vol' else vol,
                       x if xaxis == 'ir' else r,
                       x if xaxis == 'dy' else q,
                       x if xaxis == 'strike' else strike,
                       x if xaxis == 'ttm' else ttm,
                       1.) for x in xrng]
        yput = [bs_pv(x if xaxis == 'spot' else spot,
                      x if xaxis == 'vol' else vol,
                      x if xaxis == 'ir' else r,
                      x if xaxis == 'dy' else q,
                      x if xaxis == 'strike' else strike,
                      x if xaxis == 'ttm' else ttm,
                      - 1.) for x in xrng]

        figure, ax = plt.subplots()

        plt.plot(xrng, ycall, 'b', label='call')
        plt.plot([float(request.args[xaxis])], [
                 bs_pv(spot, vol, r, q, strike, ttm, 1.)], 'bo')
        plt.plot(xrng, yput, '--g', label='put')
        plt.plot([float(request.args[xaxis])], [
                 bs_pv(spot, vol, r, q, strike, ttm, -1.)], 'go')
        plt.legend(loc='best')
        plt.title('Black-Scholes')

        response = {'mpld3_data': mpld3.fig_to_dict(figure)}

        plt.close()

        return json.dumps(response)

    except Exception as e:
        return error_response(e)


@app.route('/heston/plot_data', methods=['GET'])
def heston_plot_data():
    try:
        spot = float(request.args['spot'])
        var0 = float(request.args['var0'])
        r = float(request.args['ir'])
        q = float(request.args['dy'])
        kappa = float(request.args['kappa'])
        theta = float(request.args['theta'])
        xi = float(request.args['xi'])
        rho = float(request.args['rho'])
        strike = float(request.args['strike'])
        ttm = float(request.args['ttm'])

        xaxis = request.args['xaxis']
        if xaxis in ['spot', 'var0', 'strike', 'kappa', 'theta', 'xi']:
            xrng = [0.7, 1.5] * np.ones(2) * float(request.args[xaxis])
        elif xaxis == 'rho':
            xrng = [-0.9, 0.9]
        elif xaxis in ['ir', 'dy']:
            xrng = [-0.03, +0.03] * np.ones(2) + float(request.args[xaxis])
        elif xaxis == 'ttm':
            xrng = [0.1, 10.]

        xrng = np.linspace(xrng[0], xrng[1])
        ycall = [heston_pv(x if xaxis == 'spot' else spot,
                           x if xaxis == 'var0' else var0,
                           x if xaxis == 'ir' else r,
                           x if xaxis == 'dy' else q,
                           x if xaxis == 'kappa' else kappa,
                           x if xaxis == 'theta' else theta,
                           x if xaxis == 'xi' else xi,
                           x if xaxis == 'rho' else rho,
                           x if xaxis == 'strike' else strike,
                           x if xaxis == 'ttm' else ttm,
                           1.) for x in xrng]
        yput = [heston_pv(x if xaxis == 'spot' else spot,
                          x if xaxis == 'var0' else var0,
                          x if xaxis == 'ir' else r,
                          x if xaxis == 'dy' else q,
                          x if xaxis == 'kappa' else kappa,
                          x if xaxis == 'theta' else theta,
                          x if xaxis == 'xi' else xi,
                          x if xaxis == 'rho' else rho,
                          x if xaxis == 'strike' else strike,
                          x if xaxis == 'ttm' else ttm,
                          - 1.) for x in xrng]

        figure, ax = plt.subplots()

        plt.plot(xrng, ycall, 'b-', label='call')
        plt.plot([float(request.args[xaxis])], [heston_pv(
            spot, var0, r, q, kappa, theta, xi, rho, strike, ttm, 1.)], 'bo')
        plt.plot(xrng, yput, 'g--', label='put')
        plt.plot([float(request.args[xaxis])], [heston_pv(
            spot, var0, r, q, kappa, theta, xi, rho, strike, ttm, -1.)], 'go')
        plt.legend(loc='best')
        plt.title('Heston')

        response = {'mpld3_data': mpld3.fig_to_dict(figure)}

        plt.close()

        return json.dumps(response)

    except Exception as e:
        return error_response(e)


@app.route('/heston/price_anal', methods=['GET'])
def heston_price_anal():
    try:
        spot = float(request.args['spot'])
        var0 = float(request.args['var0'])
        r = float(request.args['ir'])
        q = float(request.args['dy'])
        kappa = float(request.args['kappa'])
        theta = float(request.args['theta'])
        xi = float(request.args['xi'])
        rho = float(request.args['rho'])
        strike = float(request.args['strike'])
        ttm = float(request.args['ttm'])

        call = heston_pv(spot, var0, r, q, kappa, theta,
                         xi, rho, strike, ttm, 1.)
        put = heston_pv(spot, var0, r, q, kappa, theta,
                        xi, rho, strike, ttm, -1.)

        result = {
            'pv_call': call,
            'pv_put': put
        }
        return json.dumps(result)
    except Exception as e:
        return error_response(e)


@app.route('/test')
def test_page():
    return render_template('test.html')


if __name__ == '__main__':
    app.run()

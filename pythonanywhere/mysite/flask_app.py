
# Flask app for pricing Vanillas in 'classical' models, e.g., BS, Heston, etc.

from flask import Flask, render_template, request, json

import datetime as dt
import scipy.stats as st
import numpy as np

import matplotlib.pyplot as plt, mpld3

from fin.heston import HestonLord, HestonParams


app = Flask(__name__)

''' classical BS '''
def bs_pv(spot,vol,r,q,strike,ttm,phi):
    fwd = spot * np.exp((r-q)*ttm)
    df = np.exp(-r*ttm)

    std = vol*np.sqrt(ttm)
    dp = np.log(fwd/strike)/std+std/2.
    dm = dp - std

    return df * phi * (fwd * st.norm.cdf(phi*dp) - strike * st.norm.cdf(phi*dm))

''' heston analytical pricer based on CF integration '''
def heston_pv(spot,var0,r,q,kappa,theta,xi,rho,strike,ttm,phi):
    params = HestonParams(spot,var0,r,q,kappa,theta,xi,rho)
    model = HestonLord(params)

    return model.vanilla(strike,ttm,phi)

@app.route('/',methods=['GET'])
def hello_world():
    return 'Hello from Flask! Page loaded on {}.'.format(dt.datetime.now())

def error_response(e):
    return json.dumps({'error':{
            'type': str(type(e)),
            'str': str(e),
            'repr':repr(e),
            'msg':e.message
        }})

@app.route('/bs',methods=['GET'])
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

@app.route('/bs/price_anal',methods=['GET'])
def bs_price_anal():
    try:
        spot = float(request.args['spot'])
        vol = float(request.args['vol'])
        r = float(request.args['ir'])
        q = float(request.args['dy'])
        strike = float(request.args['strike'])
        ttm = float(request.args['ttm'])

        spotAnnualRange = spot * np.exp(vol*st.norm.ppf([0.005,0.995]))
        call = bs_pv(spot,vol,r,q,strike,ttm,1.)
        put = bs_pv(spot,vol,r,q,strike,ttm,-1.)

        result = {
            'spot_annual_range_99':list(spotAnnualRange),
            'pv_call':call,
            'pv_put':put
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
            xrange = [0.7, 1.5] * np.ones(2) * float(request.args[xaxis])
        elif xaxis in ['ir', 'dy']:
            xrange = [-0.03, +0.03] * np.ones(2) + float(request.args[xaxis])
        elif xaxis == 'ttm':
            xrange = [0.1, 10.]

        xrange = np.linspace(xrange[0], xrange[1])
        ycall = [bs_pv(x if xaxis == 'spot' else spot,
                   x if xaxis == 'vol' else vol,
                   x if xaxis == 'ir' else r,
                   x if xaxis == 'dy' else q,
                   x if xaxis == 'strike' else strike,
                   x if xaxis == 'ttm' else ttm,
                   1.) for x in xrange]
        yput = [bs_pv(x if xaxis == 'spot' else spot,
                   x if xaxis == 'vol' else vol,
                   x if xaxis == 'ir' else r,
                   x if xaxis == 'dy' else q,
                   x if xaxis == 'strike' else strike,
                   x if xaxis == 'ttm' else ttm,
                   - 1.) for x in xrange]

        figure, ax = plt.subplots()

        plt.plot(xrange, ycall, 'b', label='call')
        plt.plot([float(request.args[xaxis])], [bs_pv(spot, vol, r, q, strike, ttm, 1.)], 'bo')
        plt.plot(xrange, yput, '--g', label='put')
        plt.plot([float(request.args[xaxis])], [bs_pv(spot, vol, r, q, strike, ttm, -1.)], 'go')
        plt.legend(loc='best')
        plt.title('Black-Scholes')

        response = {'mpld3_data':mpld3.fig_to_dict(figure)}

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
            xrange = [0.7, 1.5] * np.ones(2) * float(request.args[xaxis])
        elif xaxis == 'rho':
            xrange = [-0.9, 0.9]
        elif xaxis in ['ir', 'dy']:
            xrange = [-0.03, +0.03] * np.ones(2) + float(request.args[xaxis])
        elif xaxis == 'ttm':
            xrange = [0.1, 10.]

        xrange = np.linspace(xrange[0], xrange[1])
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
                   1.) for x in xrange]
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
                   - 1.) for x in xrange]

        figure, ax = plt.subplots()

        plt.plot(xrange, ycall, 'b-', label='call')
        plt.plot([float(request.args[xaxis])], [heston_pv(spot, var0, r, q, kappa, theta, xi, rho, strike, ttm, 1.)], 'bo')
        plt.plot(xrange, yput, 'g--', label='put')
        plt.plot([float(request.args[xaxis])], [heston_pv(spot, var0, r, q, kappa, theta, xi, rho, strike, ttm, -1.)], 'go')
        plt.legend(loc='best')
        plt.title('Heston')

        response = {'mpld3_data':mpld3.fig_to_dict(figure)}

        plt.close()

        return json.dumps(response)

    except Exception as e:
        return error_response(e)


@app.route('/heston/price_anal',methods=['GET'])
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

        call = heston_pv(spot,var0,r,q,kappa,theta,xi,rho,strike,ttm,1.)
        put = heston_pv(spot,var0,r,q,kappa,theta,xi,rho,strike,ttm,-1.)

        result = {
            'pv_call':call,
            'pv_put':put
            }
        return json.dumps(result)
    except Exception as e:
        return error_response(e)


@app.route('/test')
def test_page():
    return render_template('test.html')


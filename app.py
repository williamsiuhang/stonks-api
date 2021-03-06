import flask
from flask import Flask, request, render_template, jsonify
import math
import yfinance as yf

print('Running economists')

app = flask.Flask(__name__)
# app.config["DEBUG"] = True


# response status
def success(data):
    res = {}
    return jsonify({
        "status": 200,
        "data": data
    })


def error(message):
    return jsonify({"status": 300}) if message is None else jsonify({"status": 300, "message": message})


# routes
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# stock summary


@app.route('/info', methods=['GET'])
def info():
    symbol = request.args.get('symbol')

    if symbol is not None:
        try:
            info = yf.Ticker(symbol).info
            return success(info)
        except:
            return error('Could not get information for ' + symbol)
    else:
        return error('Symbol not specified')


# stock summary
@app.route('/history', methods=['GET'])
def history():
    symbol = request.args.get('symbol')
    # period = request.args.get('period')

    if symbol is not None:
        try:
            info = yf.Ticker(symbol).ticker.history(period="max")
            print(info)
            return success(symbol)
        except:
            return error('Could not get history for ' + symbol)
    else:
        return error('Symbol not specified')

# option dates


@app.route('/options', methods=['GET'])
def options():
    symbol = request.args.get('symbol')

    if symbol is not None:
        try:
            options = list(yf.Ticker(symbol).options)
            return success(options) if len(options) > 0 else error('No options found for symbol ' + symbol)
        except:
            return error('Could not get options information for ' + symbol)
    else:
        return error('Symbol not specified')

# option chain


@app.route('/optionchain', methods=['GET'])
def optionchain():
    symbol = request.args.get('symbol')
    date = request.args.get('date')

    # pandas dataframe into key / value array
    def normalize_options(option, headers):
        normalized = {}
        for i, categoryVal in enumerate(option):
            normalized[headers[i]] = categoryVal

            # Default to 0 if NaN
            if(headers[i] in ['ask', 'bid', 'change', 'impliedVolatility', 'lastPrice', 'openInterest', 'percentChange', 'strike', 'volume']):
                if(math.isnan(categoryVal)):
                    normalized[headers[i]] = 0

            # BUG fix: currency is NaN sometimes, when it should be a string | just ignore it for now
            # Need to look into yfinance fork for better NaN handling
            if(headers[i] == 'currency'):
              normalized[headers[i]] = 0

        return normalized

    if symbol and date:
        try:
            panda_df = yf.Ticker(symbol).option_chain(date)

            headers = list(panda_df[0])

            calls = panda_df[0].values.tolist()
            puts = panda_df[1].values.tolist()

            normalized_calls = [normalize_options(
                option, headers) for option in calls]
            normalized_puts = [normalize_options(
                option, headers) for option in puts]

            return success({'calls': normalized_calls, 'puts': normalized_puts})
        except:
            return error('Could not get option chain for ' + symbol + ' with date ' + date)
    else:
        return error('Symbol or date not specified')


if __name__ == "__main__":
    app.run(host='0.0.0.0')

    # nodemon --exec flask run

import requests
import json
import pandas as pd
import statistics
from scipy.stats import linregress

base = 'https://api.binance.com'

artur = [{'asset': 'BTC', 'size': 0.00034056}, {'asset': 'BNB', 'size': 0.15504947}, {'asset': 'LINK', 'size': 2.35},
         {'asset': 'XRP', 'size': 61.89037}, {'asset': 'ADA', 'size': 46.12836716},
         {'asset': 'MATIC', 'size': 23.32750052}, {'asset': 'DOGE', 'size': 319.0},
         {'asset': 'SOL', 'size': 0.43031736}, {'asset': 'DOT', 'size': 2.47273122},
         {'asset': 'LUNA', 'size': 0.52053538}, {'asset': 'AVAX', 'size': 0.57067556},
         {'asset': 'NEAR', 'size': 1.80215012}, {'asset': 'CKB', 'size': 3008.0}]


yara = [{'asset': 'BTC', 'size': 0.00223647}, {'asset': 'LTC', 'size': 0.72137087}, {'asset': 'ETH', 'size': 0.027293},
        {'asset': 'BNB', 'size': 0.23254059}, {'asset': 'LINK', 'size': 6.0395},
        {'asset': 'ETC', 'size': 2.77}, {'asset': 'XRP', 'size': 118.778}, {'asset': 'ADA', 'size': 85.1},
        {'asset': 'VET', 'size': 1256.7}, {'asset': 'USDC', 'size': 1131.0}, {'asset': 'MATIC', 'size': 51.9},
        {'asset': 'ATOM', 'size': 3.39}, {'asset': 'DOGE', 'size': 691.2}, {'asset': 'XTZ', 'size': 22.6},
        {'asset': 'BCH', 'size': 0.23}, {'asset': 'BRL', 'size': 0.00467}, {'asset': 'SOL', 'size': 0.93},
        {'asset': 'COMP', 'size': 0.808969}, {'asset': 'MKR', 'size': 0.047896}, {'asset': 'SNX', 'size': 15.89872},
        {'asset': 'DOT', 'size': 4.48}, {'asset': 'RUNE', 'size': 16.7986}, {'asset': 'LUNA', 'size': 1.0887},
        {'asset': 'UNI', 'size': 9.0595}, {'asset': 'AVAX', 'size': 0.9993}, {'asset': 'SCRT', 'size': 17.3},
        {'asset': 'CAKE', 'size': 12.43928}, {'asset': 'NEAR', 'size': 7.0}, {'asset': 'AAVE', 'size': 0.60595},
        {'asset': 'GRT', 'size': 221.0}]


endpoints = {
    'klines': '/api/v3/klines',
    '24hrTicker': '/api/v3/ticker/24hr',
}


def get_24hr_ticker(symbol: str):
    url = base + endpoints['24hrTicker'] + "?symbol=" + symbol + 'USDT'
    last = requests.get(url).json()['lastPrice']
    return last


def get_symbol_var(symbol: str, interval: str):
    params = '?&symbol=' + symbol + '&interval=' + interval

    url = base + endpoints['klines'] + params

    # download data
    data = requests.get(url)
    dictionary = json.loads(data.text)[-366:]

    y = 0
    for x in dictionary:

        if y == 0:

            del x[5::]
            del x[1:4]
            x.append(0)
            y = float(x[1])

        else:

            del x[5::]
            del x[1:4]
            var = float(x[1]) / y - 1
            x.append(var)
            y = float(x[1])

    # put in dataframe and clean-up
    df = pd.DataFrame.from_dict(dictionary)

    # rename columns
    col_names = ['time', 'close', 'var']
    df.columns = col_names

    # transform values from strings to floats
    for col in col_names:
        df[col] = df[col].astype(float)

    df['time'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format=True)

    return df


btc = get_symbol_var('BTCUSDT', '1d')

total = 0
for s in artur:
    print(s['asset'])

    s['price'] = float(get_24hr_ticker(s['asset']))
    s['total'] = s['size'] * s['price']
    total += s['total']


beta_weighted = 0


for s in artur:
    print(s['asset'])

    s['position'] = s['total'] / total
    s['daily_vol'] = statistics.stdev(list(get_symbol_var(s['asset'] + 'USDT', '1d')['var']))
    s['beta'] = linregress(btc['var'][1::], get_symbol_var(s['asset'] + 'USDT', '1d')['var'][1::])[0]
    s['beta_weighted'] = s['beta'] * s['position']
    beta_weighted += s['beta'] * s['position']

dataf = pd.DataFrame(yara)
dataf.to_excel('Hedge.xlsx', index=False)

print(beta_weighted)

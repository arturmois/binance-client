import requests
import json
import pandas as pd

base = 'https://api.binance.com'

endpoints = {
    'order': '/api/v3/order',
    'testOrder': '/api/v3/order/test',
    'klines': '/api/v3/klines',
    'exchangeInfo': '/api/v3/exchangeInfo',
    '24hrTicker': '/api/v3/ticker/24hr',
    'account': '/api/v3/account'
}


def get(url, params=None, headers=None) -> dict:
    """ Makes a Get Request """

    try:
        response = requests.get(url, params=params, headers=headers)
        data = json.loads(response.text)
        data['url'] = url
    except Exception as e:
        print("Exception occured when trying to access " + url)
        print(e)
        data = {'code': '-1', 'url': url, 'msg': e}
    return data


def post(url, params=None, headers=None) -> dict:
    """ Makes a Post Request """

    try:
        response = requests.post(url, params=params, headers=headers)
        data = json.loads(response.text)
        data['url'] = url
    except Exception as e:
        print("Exception occured when trying to access " + url)
        print(e)
        data = {'code': '-1', 'url': url, 'msg': e}
    return data


def get_24hr_ticker(self, symbol: str):
    url = self.base + self.endpoints['24hrTicker'] + "?symbol=" + symbol
    return self.get(url)


def get_symbol_var(symbol: str, interval: str, months: int):
    params = '?&symbol=' + symbol + '&interval=' + interval

    url = base + endpoints['klines'] + params

    # download data
    data = requests.get(url)
    dictionary = json.loads(data.text)[-months - 1:]

    wallet = 0
    aport = 100
    for x in dictionary:
        del x[5::]
        del x[2:4]
        var = float(x[2]) / float(x[1]) - 1
        x.append(var)
        x.append(aport)
        wallet += aport
        wallet += wallet * var
        x.append(wallet)

    # put in dataframe and clean-up
    df = pd.DataFrame.from_dict(dictionary)

    # rename columns
    col_names = ['time', 'open', 'close', 'var', 'aport', 'wallet']
    df.columns = col_names

    # transform values from strings to floats
    for col in col_names:
        df[col] = df[col].astype(float)

    df['time'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format=True)
    df.to_excel('retorno.xlsx', index=False)

    return df


retorno = get_symbol_var('SOLUSDT', '1M', 24)

print(retorno)

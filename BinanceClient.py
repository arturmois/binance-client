import requests
import json
import decimal
import hmac
import time
import hashlib
import pandas as pd

request_delay = 1000
invest_rate = 0.7


class BinanceClient:

    def __init__(self, filename=None):

        self.base = 'https://api.binance.com'

        self.endpoints = {
            'order': '/api/v3/order',
            'testOrder': '/api/v3/order/test',
            'klines': '/api/v3/klines',
            'exchangeInfo': '/api/v3/exchangeInfo',
            '24hrTicker': '/api/v3/ticker/24hr',
            'account': '/api/v3/account'
        }
        self.account_access = False

        if filename is None:
            return

        f = open(filename, "r")
        contents = []
        if f.mode == 'r':
            contents = f.read().split('\n')

        self.binance_keys = dict(api_key=contents[0], secret_key=contents[1])

        self.headers = {"X-MBX-APIKEY": self.binance_keys['api_key']}

        self.account_access = True

    @staticmethod
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

    @staticmethod
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

    @classmethod
    def float_to_string(cls, f: float):
        """ Converts the given float to a string, without resorting to the scientific notation """

        ctx = decimal.Context()
        ctx.prec = 12
        d1 = ctx.create_decimal(repr(f))
        return format(d1, 'f')

    def sign_request(self, params: dict):
        """ Signs the request to the Binance API """

        query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
        signature = hmac.new(self.binance_keys['secret_key'].encode('utf-8'), query_string.encode('utf-8'),
                             hashlib.sha256)
        params['signature'] = signature.hexdigest()

    def get_account_data(self) -> dict:
        """ Gets Balances & Account Data """

        url = self.base + self.endpoints["account"]

        params = {
            'recvWindow': 6000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }
        self.sign_request(params)

        print(url, params, self.headers)

        return self.get(url, params, self.headers)

    def get_trading_symbols(self, quote_assets: list = None):
        """ Gets All symbols which are tradable (currently) """

        url = self.base + self.endpoints["exchangeInfo"]
        data = self.get(url)
        if data.__contains__('code'):
            return []

        symbols_list = []
        for pair in data['symbols']:
            if pair['status'] == 'TRADING':
                if quote_assets is not None and pair['quoteAsset'] in quote_assets:
                    symbols_list.append(pair['symbol'])

        return symbols_list

    def get_24hr_ticker(self, symbol: str):
        url = self.base + self.endpoints['24hrTicker'] + "?symbol=" + symbol
        return self.get(url)

    def get_symbol_klines(self, symbol: str, interval: str, limit: int = 1000, end_time=False):
        """ Gets trading data for one symbol """

        if limit > 1000:
            return self.get_symbol_klines_extra(symbol, interval, limit, end_time)

        params = '?&symbol=' + symbol + '&interval=' + interval + '&limit=' + str(limit)
        if end_time:
            params = params + '&endTime=' + str(int(end_time))

        url = self.base + self.endpoints['klines'] + params

        # download data
        data = requests.get(url)
        dictionary = json.loads(data.text)

        # put in dataframe and clean-up
        df = pd.Dataframe.from_dict(dictionary)
        df = df.drop(range(6, 12), axis=1)

        # rename columns
        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        df.columns = col_names

        # transform values from strings to floats
        for col in col_names:
            df[col] = df[col].astype(float)

        df['date'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format=True)

        return df

    def get_symbol_klines_extra(self, symbol: str, interval: str, limit: int = 1000, end_time=False):
        # Basicall, we will be calling the GetSymbolKlines as many times as we need
        # in order to get all the historical data required (based on the limit parameter)
        # and we'll be merging the results into one long dataframe.

        repeat_rounds = 0
        if limit > 1000:
            repeat_rounds = int(limit / 1000)
        initial_limit = limit % 1000
        if initial_limit == 0:
            initial_limit = 1000
        # First, we get the last initial_limit candles, starting at end_time and going
        # backwards (or starting in the present moment, if end_time is False)
        df = self.get_symbol_klines(symbol, interval, limit=initial_limit, end_time=end_time)
        while repeat_rounds > 0:
            # Then, for every other 1000 candles, we get them, but starting at the beginning
            # of the previously received candles.
            df2 = self.get_symbol_klines(symbol, interval, limit=1000, end_time=df['time'][0])
            df = df2.append(df, ignore_index=True)
            repeat_rounds = repeat_rounds - 1

        return df

    def place_order(self, symbol: str, side: str, type: str, quantity: float = 0, price: float = 0, test: bool = True):
        """ Places an order on Binance """

        params = {
            'symbol': symbol,
            'side': side,  # BUY or SELL
            'type': type,  # MARKET, LIMIT, STOP LOSS etc
            'quoteOrderQty': quantity,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        if type != 'MARKET':
            params['timeInForce'] = 'GTC'
            params['price'] = BinanceClient.float_to_string(price)

        self.sign_request(params)

        if test:
            url = self.base + self.endpoints['testOrder']
        else:
            url = self.base + self.endpoints['order']

        return self.post(url, params=params, headers=self.headers)

    def market_order(self, symbol: str, side: str, quantity: float = 0, test: bool = True):
        """ Places an order on Binance """

        params = {
            'symbol': symbol,
            'side': side,  # BUY or SELL
            'type': 'MARKET',
            'quoteOrderQty': quantity,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        if test:
            url = self.base + self.endpoints['testOrder']
        else:
            url = self.base + self.endpoints['order']

        return self.post(url, params=params, headers=self.headers)

    def get_account_balances(self):

        url = self.base + self.endpoints["account"]

        params = {
            'recvWindow': 6000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }
        self.sign_request(params)

        balances = self.get(url, params, self.headers)['balances']

        account_balances = []

        for balance in balances:

            if balance['asset'] not in ['NFT', 'SOLO', 'BETH']:

                if balance['asset'] == 'USDC':

                    balance['size'] = float(balance.pop('free'))
                    del balance['locked']
                    account_balances.append(balance)

                else:

                    if float(balance['free']) > 0:

                        try:

                            balance['size'] = float(balance.pop('free'))
                            del balance['locked']
                            account_balances.append(balance)

                        except Exception as e:
                            print(e)

        balances = pd.DataFrame(account_balances)
        balances.to_excel('report.xlsx', index=False)
        return account_balances

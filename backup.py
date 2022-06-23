from BinanceClient import BinanceClient
import pandas as pd

exchange = BinanceClient('bin_credentials.txt')
spot = exchange.get_account_balances()


def staking(xlsx):
    staking_xlsx = pd.read_excel('staking.xlsx')

    staking = []
    for x in range(len(staking_xlsx)):
        staking.append({'asset': staking_xlsx["asset"][x], 'size': float(staking_xlsx['size'][x])})

    spot_staking = spot + staking

    balances = []
    for x in spot:
        asset = {'asset': x['asset'], 'size': x['size']}
        for y in staking:
            if y['asset'] == x['asset']:
                asset['size'] += y['size']
        balances.append(asset)

    print(balances)

# def main():
#     exchange = BinanceClient('bin_credentials.txt')
#     balances = exchange.get_account_balances()
#     print(balances)
#
#
# if __name__ == '__main__':
#     main()

    def rebalance(self, balances):

        print('rebalance...')

        total_assets = len(balances) - 1
        total_usd = 0
        usdt = 0

        for balance in balances:

            if balance['asset'] != 'USDC':

                if usdt < total_usd * 0.3:

                    # se o ativo ficar $11 abaixo do rebalanceamento, comprar
                    if (total_usd * invest_rate / total_assets) - balance['usd'] > 11:
                        print(balance['asset'], (total_usd * invest_rate / total_assets) - balance['usd'])
                        symbol = balance['asset'] + 'USDT'
                        side = 'BUY'
                        quantity = round((total_usd * invest_rate / total_assets) - balance['usd'])

                        params = {
                            'symbol': symbol,
                            'side': side,  # BUY or SELL
                            'type': 'MARKET',
                            'quoteOrderQty': quantity,
                            'recvWindow': 5000,
                            'timestamp': int(round(time.time() * 1000)) + request_delay
                        }

                        self.sign_request(params)

                        url = self.base + self.endpoints['order']

                        response = self.post(url, params=params, headers=self.headers)
                        print(response)
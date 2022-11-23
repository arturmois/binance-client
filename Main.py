from BinanceClient import BinanceClient
import pandas as pd
import requests

fiat = ['USDT', 'BRL']


def extract_portfolio(exchange, xlsx):
    spot = exchange.get_account_balances()

    staking_xlsx = pd.read_excel(xlsx)

    staking = []
    for x in range(len(staking_xlsx)):
        staking.append({'asset': staking_xlsx["asset"][x], 'size': float(staking_xlsx['size'][x])})

    balances = []
    for x in spot:
        asset = {'asset': x['asset'], 'size': x['size']}
        for y in staking:
            if y['asset'] == x['asset']:
                asset['size'] += y['size']
        balances.append(asset)

    return balances


def rebalance(balances):
    print('rebalance...')

    total_usd = 0
    usdc = 0
    for x in balances:
        if x['asset'] in fiat:

            print('not value')
        else:
            usd = x['size'] * float(
                requests.get(
                    'https://api.binance.com/api/v3/ticker/24hr?symbol=' + x['asset'] + 'USDT'
                ).json()['lastPrice']

            )

        if x['asset'] == 'USDT':
            x['usd'] = usd
            usdc = x['size']
        else:
            x['usd'] = usd

        total_usd += usd

    for x in balances:
        x['%'] = x['usd'] / total_usd

    balances = pd.DataFrame(balances)
    balances.to_excel('report.xlsx', index=False)

    for balance in balances:
        print(balance)
        if balance['asset'] != 'USDT':

            if usdc < total_usd * 0.3:
                print('here')


def main():
    exchange = BinanceClient('credentials.txt')
    data = exchange.get_account_balances()
    print(data)

if __name__ == '__main__':
    main()

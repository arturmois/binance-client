from BinanceClient import BinanceClient
import pandas as pd


def stract(exchange, xlsx):
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


def main():
    exchange = BinanceClient('bin_credentials.txt')
    stake = stract(exchange, 'staking.xlsx')
    print(len(stake))


if __name__ == '__main__':
    main()

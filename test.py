from web3 import Web3

infura_url = "https://mainnet.infura.io/v3/f40ae3b8c8714803b3969cae331048ff"
web3 = Web3(Web3.HTTPProvider(infura_url))

print(web3.isConnected())


import requests
import pandas as pd
import json

def request_data(function_api, symbol, key):
    url = 'https://financialmodelingprep.com/api/v3/{function_api}/{symbol}?period=annual&apikey={key}'.format( function_api=function_api, symbol=symbol, key=key)
    #url = 'https://www.alphavantage.co/query?function={function_api}&symbol={symbol}&interval=5min&apikey={key}'.format( function_api=function_api, symbol=symbol, key=key)
    r = requests.get(url)
    data = r.json()
    with open('{symbol}_{function_api}.json'.format( function_api=function_api, symbol=symbol, key=key), 'w') as fp:
        json.dump(data, fp)

request_data("cash-flow-statement", "IBM", "rh8MeZMIpnpD1JcI6zFuPYd0nDGxXr2L")
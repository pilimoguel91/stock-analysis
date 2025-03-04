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


# Request API Key from https://www.alphavantage.co/support/#api-key
request_data("quote", "IBM", )



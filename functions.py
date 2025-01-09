import pandas as pd
import json


with open('IBM_CASH_FLOW.json') as json_cashflow_data: ### Missing: convert to variables for different stock symbols
    data_cashflow = json.load(json_cashflow_data)
    df_cashflow = pd.DataFrame(data_cashflow['annualReports'])
    df_cashflow['year'] = df_cashflow['fiscalDateEnding'][:4]
    df_cashflow

with open('IBM_OVERVIEW.json') as json_overview_data: ### Missing: convert to variables for different stock symbols
    data_overview = json.load(json_overview_data)
    df_overview = pd.DataFrame(data_overview, index=[0])
    df_overview


print(df_cashflow['year'])
# def cash_4_owners():
#    df_cashflow['cash_4_owners'] = df_cashflow['operatingCashflow'] - df_cashflow['capitalExpenditures']
#    df_overview['ten_cap'] = df_overview['MarketCapitalization'] /  df_cashflow['cash_4_owners']
#    df_overview['ten_cap']

# cash_4_owners()


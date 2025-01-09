import pandas as pd
import json


with open('IBM_CASH_FLOW.json') as json_cashflow_data: ### Missing: convert to variables for different stock symbols
    data_cashflow = json.load(json_cashflow_data)
    df_cashflow = pd.DataFrame(data_cashflow['annualReports'])
    fiscalDateEnding = pd.to_datetime(df_cashflow['fiscalDateEnding'])
    df_cashflow['year'] = pd.DatetimeIndex(fiscalDateEnding).year
    df_cashflow['operatingCashflow'] = pd.to_numeric(df_cashflow['operatingCashflow'], errors="coerce")
    df_cashflow['capitalExpenditures'] = pd.to_numeric(df_cashflow['capitalExpenditures'], errors="coerce")

with open('IBM_OVERVIEW.json') as json_overview_data: ### Missing: convert to variables for different stock symbols
    data_overview = json.load(json_overview_data)
    df_overview = pd.DataFrame(data_overview, index=[0])    
    df_overview['MarketCapitalization'] = pd.to_numeric(df_overview['MarketCapitalization'], errors="coerce")
    LatestQuarter = pd.to_datetime(df_overview['LatestQuarter'])
    df_overview['previous_year'] = (pd.DatetimeIndex(LatestQuarter).year - 1)


def cash_4_owners(year = int(df_overview['previous_year'])):
    df_cashflow['cash_4_owners'] = df_cashflow['operatingCashflow'] - df_cashflow['capitalExpenditures']
    df_cashflow_filter = df_cashflow.loc[df_cashflow['year'] == year]
    df_overview['ten_cap'] = (df_overview['MarketCapitalization'] /  df_cashflow_filter['cash_4_owners'])
    print(df_overview, df_cashflow)


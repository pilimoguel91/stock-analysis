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

# Cashflow function
def cash_4_owners(year = int(df_overview['previous_year'].iloc[0])):
# Cash for owners calculates the cash available after capital expenditures, and is used to calculate the 10cap by using the market cap of the company.
    df_cashflow['cash_4_owners'] = df_cashflow['operatingCashflow'] - df_cashflow['capitalExpenditures']
    df_cashflow_filter = df_cashflow.loc[df_cashflow['year'] == year]
# 10 cap is a yield return percentage based on the cash available divided by the company total value, above 10 is a good investment
    df_overview['ten_cap'] = (df_cashflow_filter['cash_4_owners'] / df_overview['MarketCapitalization'])
    yield_return = df_overview['ten_cap'].iloc[0]
# Dummy print for now, we should pass this result to the model later, of course
    if (df_overview['ten_cap'] > 0.10).all():
        print(df_overview["Symbol"] + " looks like a good investment with a " + str(df_overview['ten_cap']) + " estimated yield return") 
    else:
        print(df_overview["Symbol"] + " doesnt look like a good investment with a " + str(yield_return) + " estimated yield return") 

cash_4_owners()
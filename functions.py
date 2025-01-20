import pandas as pd
import json
import numpy as np


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
    if (df_overview['ten_cap'] >= 0.10).all(): 
        print('{} looks like a good investment with a {} estimated yield return'.format(df_overview["Symbol"], str(df_overview['ten_cap']))) 
    else: 
        print('{} doesnt look like a good investment with a {} estimated yield return'.format(df_overview["Symbol"], str(yield_return)))

cash_4_owners()

# Net Present Value (NPV) function 
# risk_free_rate/discounted rate: accounts for the amount the investor could earn without risk (bank returns or government programs)
# cashflow_growth: how much will the cashflow grow yoy in the next years_projection --- I think this should be calculated based on previous data, as shouldn't be the same for every company 
def npv(cashflow_growth= .10, year = int(df_overview['previous_year'].iloc[0]), years_projection=10):
    # get last year cashflow
    last_year = df_cashflow.loc[df_cashflow['year'] == year]
    
    # do a linear interpolation of the cashflow (equal growth for each year)         
    def interpolate(initial_value, terminal_value, years_projection=10):
        return np.linspace(initial_value, terminal_value, years_projection)
    
    df_cashflow_sort = df_cashflow.sort_values("year", ascending=True)

    years = range(df_cashflow_sort["year"].iloc[-1]+1, df_cashflow_sort["year"].iloc[-1] + years_projection + 1)

    df_proj_cashflow = pd.DataFrame(index=years)

    # execute linear interpolation
    df_proj_cashflow["cashflow"] = interpolate(last_year['cash_4_owners'], cashflow_growth, years_projection)
    
    # calculate net present value
    def calculate_present_value(cash_flows, risk_free_rate = .04):
    # Calculate the present value using: PV = CF / (1 + r)^t + TV/(1 + r)^T

        present_values_cf = [cf / (1 + risk_free_rate) ** t for t, cf in enumerate(cash_flows, start=1)]
        return present_values_cf

    df_proj_cashflow["cashflow"] = calculate_present_value(df_proj_cashflow["cashflow"].values)
    print(df_proj_cashflow)


npv()
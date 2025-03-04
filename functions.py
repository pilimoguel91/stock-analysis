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
with open('IBM_quote.json') as json_overview_data: ### Missing: convert to variables for different stock symbols
    data_overview = json.load(json_overview_data)
    df_quote = pd.DataFrame(data_overview, index=[0])
    price = pd.to_numeric(df_quote['price'], errors="coerce")


# Cashflow function
def cash_4_owners(year = int(df_overview['previous_year'].iloc[0])):
# Cash for owners calculates the cash available after capital expenditures, and is used to calculate the 10cap by using the market cap of the company.
    df_cashflow['cash_4_owners'] = df_cashflow['operatingCashflow'] - df_cashflow['capitalExpenditures']
    df_cashflow_filter = df_cashflow.loc[df_cashflow['year'] == year]

# Getting different growth
    df_cashflow_sorted = df_cashflow.sort_values('year')
    df_cashflow_sorted["cashflow_growth_yoy"] = round(df_cashflow_sorted['cash_4_owners'].pct_change(), 2)
    df_cashflow_sorted["cashflow_growth_10y"] = df_cashflow_sorted['cash_4_owners'].pct_change(10)
    df_cashflow_sorted["cashflow_growth_10y_avg"] = df_cashflow_sorted["cashflow_growth_10y"].mean()
    df_cashflow_sorted["cashflow_growth_yoy_avg"] = df_cashflow_sorted["cashflow_growth_yoy"].mean()

## Ten Cap: This would be the first analysis based on the company cashflow, if the company has a cap of 10 or more, it is a recommended buy.
    df_overview['ten_cap'] = (df_cashflow_filter['cash_4_owners'] / df_overview['MarketCapitalization'])
    yield_return = df_overview['ten_cap'].iloc[0]
# Dummy print for now, we should pass this result to the model later, of course
    if (df_overview['ten_cap'] >= 0.10).all(): 
        print('{} looks like a good investment with a {} estimated yield return'.format(df_overview["Symbol"], str(df_overview['ten_cap']))) 
    else: 
        print('{} doesnt look like a good investment with a {} estimated yield return'.format(df_overview["Symbol"], str(yield_return)))
    return df_cashflow_sorted
df_cashflow_sorted = cash_4_owners()

print(df_cashflow_sorted)

## Calculate the stock value: This would be the second analysis based on company cashflow. If the desired price is equal or greater than the actual price, it is a recommended buy.

# Net Present Value (NPV) function
# risk_free_rate/discounted rate: accounts for the amount the investor could earn without risk (bank returns or government programs)
# cashflow_growth: how much will the cashflow grow yoy in the next years_projection --- I think this should be calculated based on previous data, as shouldn't be the same for every company 
def npv(cashflow_growth= 0.0, years_projection=10, df=df_cashflow_sorted):
    # get last year cashflow
    last_year = df.iloc[-1, :]
    
    # do a linear interpolation of the cashflow (equal growth for each year)         
    def interpolate(initial_value, terminal_value, years_projection=10):
        return np.linspace(initial_value, terminal_value, years_projection)

    years = range(df["year"].iloc[-1]+1, df["year"].iloc[-1] + years_projection + 1)

    df_proj_cashflow = pd.DataFrame(index=years)
    initial_value = df["cashflow_growth_10y_avg"].iloc[-1]

    # execute linear interpolation
    df_proj_cashflow["cashflow_growth"] = interpolate(initial_value, cashflow_growth, years_projection)

    # df_proj_cashflow["cashflow"] = 1 * (1 + df_proj_cashflow["cashflow_growth"])
    df_proj_cashflow["cashflow"] = last_year["cash_4_owners"] * (1+df_proj_cashflow["cashflow_growth"]).cumprod()

    # calculate net present value
    def calculate_present_value(cash_flows, risk_free_rate = .04):
    # Calculate the present value using: PV = CF / (1 + r)^t + TV/(1 + r)^T

        present_values_cf = [cf / (1 + risk_free_rate) ** t for t, cf in enumerate(cash_flows, start=1)]
        return present_values_cf

    df_proj_cashflow["npv"] = calculate_present_value(df_proj_cashflow["cashflow"].values, 0.04)

    return df_proj_cashflow

df_proj_cashflow = npv(0.10, 10, df_cashflow_sorted)
print(df_proj_cashflow)

# Calculate the desired price per share based on the NPV and the number of shares
def buy_price_per_share(npv = df_proj_cashflow["npv"].iloc[-1], num_shares = df_overview['SharesOutstanding'], terminal_growth = 0, expected_rr = .22):
    # The defined present value of the company needs to be divided by the number of shares, so we get the price per share
    terminal_value = npv * (1 + terminal_growth) / (expected_rr - terminal_growth)
    desired_buy_price = terminal_value / num_shares.astype(int)
    return desired_buy_price.astype(float)

desired_buy_price = buy_price_per_share()

# Compare the desired price per share to the actual price per share
def compare_buy_price_actual_price(buy_price = desired_buy_price, actual_price = price):
    if (buy_price >= actual_price).item():
        print("Desired price is {} and actual price is {} Stock value is good, recommend buying".format(str(buy_price), str(actual_price)))
    elif (actual_price >= buy_price * 2).item():
        print("Desired price is {} and actual price is {} Price is more than twice as expensive as stock value, don't recommend buying".format(str(buy_price),
                                                                                                        str(actual_price)))
    else:
        print(
            "Desired price is {} and actual price is {} Price is more expensive than stock value, but still acceptable".format(
                str(buy_price),
                str(actual_price)))

recommendation = compare_buy_price_actual_price()

### Instead of prints we need to assing a variable with the recommendation, so we can run it for multiple stocks to make analysis that will help us build the model. We would have another 7 metrics (9 in total) so we can define the model based on the best combo.
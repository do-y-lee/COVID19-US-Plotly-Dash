import pandas as pd
import numpy as np
from covid.transform.covid_counties_ts import complete_counties_ts
from covid.stats import states_stats


def complete_states_ts():
    """
    State-level time series data of confirmed cases, deaths, CC per 100k, deaths per 100k,
    confirmed infection rate, death rate.

    :return: df_states_ts dataframe
    """

    # import county-level time series confirmed cases and death dataframe
    df_counties_ts = complete_counties_ts()
    df_states_stats = states_stats()

    # group confirmed cases by state - rolling up county level to state level
    df_conf_states_ts = df_counties_ts.groupby(['State/Territory', 'Date'])['Confirmed Cases'].sum().reset_index()

    # merge df_states_stats
    df_conf_states_ts = pd.merge(df_conf_states_ts, df_states_stats, how='left', on='State/Territory')

    # merge state level deaths data
    df_deaths_states_ts = df_counties_ts.groupby(['State/Territory', 'Date'])['Deaths'].sum().reset_index()
    df_states_ts = pd.merge(df_conf_states_ts, df_deaths_states_ts, how='left', on=['State/Territory', 'Date'])

    # create metrics: pop_factor, cc per 100k, deaths per 100k, death rate, confirmed infection rate
    df_states_ts['pop_factor'] = df_states_ts['Population'].div(100000)

    df_states_ts['Cases per 100k'] = df_states_ts['Confirmed Cases'].div(
        df_states_ts['pop_factor']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(0)

    df_states_ts['Confirmed Infection Rate (%)'] = 100 * df_states_ts['Confirmed Cases'].div(
        df_states_ts['Population']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(6)

    df_states_ts['Deaths per 100k'] = df_states_ts['Deaths'].div(
        df_states_ts['pop_factor']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(0)

    df_states_ts['Death Rate (%)'] = 100 * df_states_ts['Deaths'].div(
        df_states_ts['Confirmed Cases']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(6)

    return df_states_ts


"""
from covid.transform.covid_states_ts import complete_states_ts
df1 = complete_states_ts()
print(df1.info())

<class 'pandas.core.frame.DataFrame'>
Int64Index: 10608 entries, 0 to 10607
Data columns (total 15 columns):
 #   Column                        Non-Null Count  Dtype         
---  ------                        --------------  -----         
 0   State/Territory               10608 non-null  object        
 1   Date                          10608 non-null  datetime64[ns]
 2   Confirmed Cases               10608 non-null  int64         
 3   Union Status                  10608 non-null  object        
 4   Code                          10608 non-null  object        
 5   lat                           10608 non-null  float64       
 6   lon                           10608 non-null  float64       
 7   Population                    10608 non-null  float64       
 8   State FIPS                    10608 non-null  object        
 9   Deaths                        10608 non-null  int64         
 10  pop_factor                    10608 non-null  float64       
 11  Confirmed Cases per 100k      10608 non-null  float64       
 12  Confirmed Infection Rate (%)  10608 non-null  float64       
 13  Deaths per 100k               10608 non-null  float64       
 14  Death Rate (%)                10608 non-null  float64       
dtypes: datetime64[ns](1), float64(8), int64(2), object(4)
memory usage: 1.3+ MB
"""

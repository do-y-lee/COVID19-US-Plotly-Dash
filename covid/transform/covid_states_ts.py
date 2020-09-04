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

    df_states_ts['Deaths per 100k'] = df_states_ts['Deaths'].div(
        df_states_ts['pop_factor']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(0)

    df_states_ts['Death Rate (%)'] = 100 * df_states_ts['Deaths'].div(
        df_states_ts['Confirmed Cases']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(6)

    return df_states_ts

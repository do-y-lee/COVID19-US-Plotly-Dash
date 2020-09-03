import pandas as pd
import numpy as np
from covid.transform.covid_states_ts import complete_states_ts


def complete_national_ts():
    # import and create state level time series data
    df_states_ts = complete_states_ts()

    # confirmed cases and deaths at national level, and merge dataframes
    df_confirmed_ts = df_states_ts.groupby('Date')['Confirmed Cases'].sum().reset_index()
    df_deaths_ts = df_states_ts.groupby('Date')['Deaths'].sum().reset_index()
    df_usa_ts = pd.merge(df_confirmed_ts, df_deaths_ts, how='left', on='Date')

    # calculate usa population for US states and District of Columbia
    df_usa_population = df_states_ts[df_states_ts['State/Territory'] != 'Puerto Rico']
    df_usa_population = df_usa_population.groupby('State/Territory')['Population'].max().sum()
    df_usa_ts['Population'] = df_usa_population
    # create pop_factor
    df_usa_ts['pop_factor'] = df_usa_ts['Population'].div(100000)

    # calculate national cc per 100k, deaths per 100k, confirmed infection rate, death rate
    df_usa_ts['Confirmed Cases per 100k'] = df_usa_ts['Confirmed Cases'].div(df_usa_ts['pop_factor']).round(1)
    df_usa_ts['Deaths per 100k'] = df_usa_ts['Deaths'].div(df_usa_ts['pop_factor']).round(1)
    df_usa_ts['Death Rate (%)'] = 100 * df_usa_ts['Deaths'].div(df_usa_ts['Confirmed Cases']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(6)
    df_usa_ts['Confirmation Infection Rate (%)'] = 100 * df_usa_ts['Confirmed Cases'].div(df_usa_ts['Population']).round(6)

    return df_usa_ts


def latest_national_snapshot():
    """last row will be the total aggregate for the USA because its cumulative"""
    df_national_ts = complete_national_ts()
    df_snapshot = df_national_ts.tail(1)

    df_snapshot = df_snapshot.loc[:, ['Population', 'Confirmed Cases', 'Deaths', 'Confirmed Cases per 100k', 'Deaths per 100k', 'Death Rate (%)']]
    df_snapshot['Death Rate (%)'] = df_snapshot['Death Rate (%)'].round(2).astype(str).apply(lambda x: x+'%')
    df_snapshot['Population'] = df_snapshot['Population'].astype(int).apply(lambda x: '{:,}'.format(x))
    df_snapshot['Confirmed Cases'] = df_snapshot['Confirmed Cases'].astype(int).apply(lambda x: '{:,}'.format(x))
    df_snapshot['Deaths'] = df_snapshot['Deaths'].astype(int).apply(lambda x: '{:,}'.format(x))

    df_snapshot['Confirmed Cases per 100k'] = df_snapshot['Confirmed Cases per 100k'].astype(int).apply(lambda x: '{:,}'.format(x))
    df_snapshot['Deaths per 100k'] = df_snapshot['Deaths per 100k'].astype(int).apply(lambda x: '{:,}'.format(x))

    df_snapshot.rename(columns={'Population': 'U.S. Population',
                                'Confirmed Cases per 100k': 'Cases per 100k',
                                'Death Rate (%)': 'Death Rate'}, inplace=True)
    return df_snapshot

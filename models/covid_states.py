import pandas as pd
import numpy as np
from models.covid_counties import CovidCounties
from models.stats import Stats


class CovidStates:
    @classmethod
    def agg_complete_states(cls) -> pd.DataFrame:
        """
        Cumulative confirmed cases and deaths by state
        :return: dataframe
        """

        # import and create base dataframes
        df_counties_agg = CovidCounties.agg_complete_counties()
        df_states_stats = Stats.states_stats()

        # sum confirmed by state
        df_confirmed_states_agg = df_counties_agg.groupby('State/Territory')['confirmed'].sum().reset_index()

        # merge states stats
        df_confirmed_states_agg = pd.merge(df_confirmed_states_agg, df_states_stats, how='left', on='State/Territory')

        # format population with separating commas
        df_confirmed_states_agg['2019 Est Pop'] = df_confirmed_states_agg['Population'].fillna(0).astype(int).apply(
            lambda x: '{:,}'.format(x))

        # create 'Confirmed Cases' column formatted with commas and keep 'confirmed' column as integer
        df_confirmed_states_agg['Confirmed Cases'] = df_confirmed_states_agg['confirmed'].apply(lambda x: '{:,}'.format(x))

        # create dataframe deaths by state
        df_deaths_states_agg = df_counties_agg.groupby('State/Territory')['deaths'].sum().reset_index()

        # merge df_confirmed_states_agg and df_deaths_states_agg
        df_states_agg = pd.merge(df_confirmed_states_agg, df_deaths_states_agg, on='State/Territory', how='left')

        # create formatted string Deaths column
        df_states_agg['Deaths'] = df_states_agg['deaths'].fillna(0).apply(lambda x: '{:,}'.format(x))

        # create population 100k factor to calculate confirmed cases per 100k and deaths per 100k
        df_states_agg['pop_factor'] = df_states_agg['Population'].div(100000).replace((np.inf, -np.inf, np.nan), (0, 0, 0))

        # calculate 'Confirmed Cases per 100k' people
        df_states_agg['cc_per_100k'] = df_states_agg['confirmed'].div(
            df_states_agg['pop_factor']).replace((np.nan, -np.inf, np.inf), (0, 0, 0)).round(0)
        # calculate 'Deaths per 100k' people
        df_states_agg['d_per_100k'] = df_states_agg['deaths'].div(
            df_states_agg['pop_factor']).replace((np.nan, np.inf, -np.inf), (0, 0, 0)).round(0)

        # create formatted hover models for Plotly US map
        df_states_agg['Cases per 100k'] = df_states_agg['cc_per_100k'].apply(lambda x: '{:,}'.format(x))
        df_states_agg['Deaths per 100k'] = df_states_agg['d_per_100k'].apply(lambda x: '{:,}'.format(x))
        df_states_agg['Death Rate (%)'] = round(100 * df_states_agg['deaths'].div(df_states_agg['confirmed']).replace((np.nan, np.inf, -np.inf), (0, 0, 0)), 4)

        remove_list = ['American Samoa', 'Federated States of Micronesia', 'Palau',
                       'Guam', 'Virgin Islands', 'Marshall Islands', 'Northern Mariana Islands']
        df_states_agg = df_states_agg.drop(df_states_agg.index[df_states_agg['State/Territory'].isin(remove_list)])

        return df_states_agg

    @classmethod
    def ts_complete_states(cls) -> pd.DataFrame:
        """
        State-level time series models of confirmed cases, deaths, CC per 100k, deaths per 100k,
        confirmed infection rate, death rate.

        :return: df_states_ts dataframe
        """

        # county-level time series confirmed cases and death dataframe
        df_counties_ts = CovidCounties.ts_complete_counties()
        df_states_stats = Stats.states_stats()

        # group confirmed cases by state - rolling up county level to state level
        df_conf_states_ts = df_counties_ts.groupby(['State/Territory', 'Date'])['Confirmed Cases'].sum().reset_index()

        # merge df_states_stats
        df_conf_states_ts = pd.merge(df_conf_states_ts, df_states_stats, how='left', on='State/Territory')

        # merge state level deaths models
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

    @classmethod
    def ts_complete_national(cls) -> pd.DataFrame:
        # state-level time series
        df_states_ts = cls.ts_complete_states()

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
        df_usa_ts['Death Rate (%)'] = 100 * df_usa_ts['Deaths'].div(
            df_usa_ts['Confirmed Cases']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(6)
        df_usa_ts['Confirmation Infection Rate (%)'] = 100 * df_usa_ts['Confirmed Cases'].div(df_usa_ts['Population']).round(6)

        return df_usa_ts

    @classmethod
    def latest_national_snapshot(cls) -> pd.DataFrame:
        # last row will be the total aggregate for the USA because its cumulative
        df_national_ts = cls.ts_complete_national()
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

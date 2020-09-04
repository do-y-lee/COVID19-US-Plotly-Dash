import pandas as pd
import numpy as np


def confirmed_counties_ts():
    # read in local confirmed csv files
    df_confirmed_us = pd.read_csv('static/data/time_series_covid19_confirmed_US.csv')

    # create initial time series df
    df_conf_counties_ts = pd.concat(
        [df_confirmed_us.loc[:, ['FIPS', 'Province_State', 'Admin2']], df_confirmed_us.iloc[:, 11:]], axis=1)

    # rename columns
    df_conf_counties_ts.rename(columns={'Province_State': 'State/Territory', 'Admin2': 'County'}, inplace=True)

    # modify FIPS column to string
    df_conf_counties_ts['FIPS'] = df_conf_counties_ts['FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(5))
    # create state_fips string column
    df_conf_counties_ts['State FIPS'] = df_conf_counties_ts['FIPS'].apply(lambda x: x[:2])

    # drop rows with these values - cruise ships, out-of-state, and non-county rows
    state_fips_remove = ['88', '99', '80', '00']
    for i in state_fips_remove:
        df_conf_counties_ts = df_conf_counties_ts.drop(
            df_conf_counties_ts.index[df_conf_counties_ts['State FIPS'] == i]
        ).reset_index(drop=True)

    # transpose the TS data with pd.melt
    df_conf_counties_ts = pd.melt(df_conf_counties_ts,
                                  id_vars=['State FIPS', 'FIPS', 'State/Territory', 'County'],
                                  var_name='Date',
                                  value_name='Confirmed Cases')
    # convert Date into datetime
    df_conf_counties_ts['Date'] = pd.to_datetime(df_conf_counties_ts['Date'])

    # create County-State column
    df_conf_counties_ts['County-State'] = df_conf_counties_ts['County'] + ', ' + df_conf_counties_ts['State/Territory']

    return df_conf_counties_ts


def deaths_counties_ts():
    # read in local deaths csv file
    df_deaths_us = pd.read_csv('static/data/time_series_covid19_deaths_US.csv')

    # create new df
    df_deaths_counties_ts = pd.concat(
        [df_deaths_us.loc[:, ['FIPS', 'Province_State', 'Admin2', 'Population']], df_deaths_us.iloc[:, 12:]], axis=1)

    # rename columns
    df_deaths_counties_ts.rename(columns={'Province_State': 'State/Territory', 'Admin2': 'County'}, inplace=True)

    # modify FIPS column
    df_deaths_counties_ts['FIPS'] = df_deaths_counties_ts['FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(5))

    # transposing the data
    df_deaths_counties_ts = pd.melt(df_deaths_counties_ts,
                                    id_vars=['FIPS', 'State/Territory', 'County', 'Population'],
                                    var_name='Date',
                                    value_name='Deaths')
    # convert Date string into Date datetime
    df_deaths_counties_ts['Date'] = pd.to_datetime(df_deaths_counties_ts['Date'])

    return df_deaths_counties_ts


def complete_counties_ts():
    df_conf_counties_ts = confirmed_counties_ts()
    df_deaths_counties_ts = deaths_counties_ts()
    df_deaths_counties_ts = df_deaths_counties_ts.loc[:, ['FIPS', 'State/Territory', 'County',
                                                          'Date', 'Population', 'Deaths']]
    join_columns = ['FIPS', 'State/Territory', 'County', 'Date']
    df_complete_counties_ts = pd.merge(df_conf_counties_ts, df_deaths_counties_ts, how='left', on=join_columns)

    # calculate 'Death Rate' by county using time series data
    df_complete_counties_ts['Death Rate (%)'] = 100 * df_complete_counties_ts['Deaths'].div(
        df_complete_counties_ts['Confirmed Cases']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(6)

    # create pop_factor (1000) to calculate 'Cases per 1000'
    df_complete_counties_ts['pop_factor'] = df_complete_counties_ts['Population'].fillna(0).div(1000)

    # calculate 'Cases per 1000' for time series
    df_complete_counties_ts['Cases per 1000'] = df_complete_counties_ts['Confirmed Cases'].div(
        df_complete_counties_ts['pop_factor']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(4)

    return df_complete_counties_ts

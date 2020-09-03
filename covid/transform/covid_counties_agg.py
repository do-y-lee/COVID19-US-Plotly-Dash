import pandas as pd
import numpy as np


def confirmed_counties_agg():
    # read csv files
    df_confirmed_us = pd.read_csv('static/data/time_series_covid19_confirmed_US.csv')

    df_county_pop = pd.read_csv('static/metadata/counties_stats.csv')
    df_county_pop = df_county_pop[['Admin2', 'Province_State', 'Population']]
    df_county_pop.rename(columns={'Province_State': 'State/Territory', 'Admin2': 'County'}, inplace=True)

    # grab only the latest date confirmed case numbers - cumulative
    df1 = df_confirmed_us.loc[:, ['FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', 'Combined_Key']]

    last_col_name = df_confirmed_us.columns.tolist()[-1]
    df2 = df_confirmed_us.loc[:, last_col_name]

    df_confirmed_counties_agg = pd.concat([df1, df2], axis=1)

    # change column name
    dt_col_name = df_confirmed_counties_agg.columns.tolist()[-1]
    df_confirmed_counties_agg.rename(columns={dt_col_name: 'confirmed',
                                              'Province_State': 'State/Territory',
                                              'Admin2': 'County',
                                              'Combined_Key': 'County-State'}, inplace=True)
    # shorten County-State column by removing US
    df_confirmed_counties_agg['County-State'] = df_confirmed_counties_agg['County-State'].apply(lambda x: x.replace(', US', '').replace(',US', ''))
    # convert FIPS into string
    df_confirmed_counties_agg['FIPS'] = df_confirmed_counties_agg['FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(5))
    # this depends on FIPS being adjusted by .zfill(5)
    df_confirmed_counties_agg['State FIPS'] = df_confirmed_counties_agg['FIPS'].apply(lambda x: x[:2])

    # create formatted Death column strings with commas
    df_confirmed_counties_agg['Confirmed Cases'] = df_confirmed_counties_agg['confirmed'].apply(lambda x: '{:,}'.format(x))

    # add in county population
    df_confirmed_counties_agg = pd.merge(df_confirmed_counties_agg, df_county_pop, how='left', on=['County', 'State/Territory'])

    # drop rows with Diamond Princess and Grand Princess and 80 out of state
    drop_list = ['88', '99', '80', '00']
    for fips in drop_list:
        df_confirmed_counties_agg = df_confirmed_counties_agg.drop(
            df_confirmed_counties_agg.index[df_confirmed_counties_agg['State FIPS'] == fips]).reset_index(drop=True)

    return df_confirmed_counties_agg


def deaths_counties_agg():
    # read csv file
    df_deaths_us = pd.read_csv('static/data/time_series_covid19_deaths_US.csv')

    # create base df
    df_deaths_counties_stg = df_deaths_us.loc[:, ['FIPS', 'Admin2', 'Province_State', 'Population', 'Lat', 'Long_']]
    # format FIPS
    df_deaths_counties_stg['FIPS'] = df_deaths_counties_stg['FIPS'].fillna(0).astype(int).apply(
        lambda x: str(x).zfill(5))
    # create state_fips column
    df_deaths_counties_stg['State FIPS'] = df_deaths_counties_stg['FIPS'].apply(lambda x: x[:2])

    # add cumulative confirmed case values
    last_col_name = df_deaths_us.columns.tolist()[-1]
    df_deaths_counties_agg = pd.concat([df_deaths_counties_stg, df_deaths_us.loc[:, last_col_name]], axis=1)

    # remove state_fips = 88 (cruise ship), 99 (cruise ship), 80 (out of state), 00 (non-counties)
    remove_state_fips = ['88', '99', '80', '00']
    for state_fips in remove_state_fips:
        df_deaths_counties_agg = df_deaths_counties_agg.drop(
            df_deaths_counties_agg.index[df_deaths_counties_agg['State FIPS'] == state_fips]).reset_index(drop=True)

    # rename columns
    dt_col_name = df_deaths_counties_agg.columns[-1]
    df_deaths_counties_agg.rename(columns={'Province_State': 'State/Territory',
                                           'Admin2': 'County',
                                           dt_col_name: 'deaths'}, inplace=True)

    # create formatted Death column strings with commas
    df_deaths_counties_agg['Deaths'] = df_deaths_counties_agg['deaths'].apply(lambda x: '{:,}'.format(x))

    # create county-state column
    df_deaths_counties_agg['County-State'] = df_deaths_counties_agg['County'] + ", " + df_deaths_counties_agg['State/Territory']

    return df_deaths_counties_agg


def complete_counties_agg():
    df_confirmed_counties_agg = confirmed_counties_agg()
    df_deaths_counties_agg = deaths_counties_agg()
    df_deaths_counties_agg = df_deaths_counties_agg.loc[:, ['State FIPS', 'FIPS', 'County', 'State/Territory', 'deaths', 'Deaths']]

    join_columns = ['State FIPS', 'FIPS', 'County', 'State/Territory']
    df_complete_counties_agg = pd.merge(df_confirmed_counties_agg, df_deaths_counties_agg, how='left', on=join_columns)

    # create metrics: death rate by county, confirmed infection rate if pop available
    df_complete_counties_agg['Death Rate (%)'] = round(100 * df_complete_counties_agg['deaths'].div(
        df_complete_counties_agg['confirmed']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)), 4)

    df_complete_counties_agg['Confirmed Infection Rate (%)'] = round(100 * df_complete_counties_agg['confirmed'].div(
        df_complete_counties_agg['Population']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)), 4)

    df_complete_counties_agg['Est Pop'] = df_complete_counties_agg['Population'].fillna(0).astype(int).apply(lambda x: '{:,}'.format(x))

    df_complete_counties_agg['pop_factor'] = df_complete_counties_agg['Population'].fillna(0).div(1000)

    df_complete_counties_agg['Cases per 1000'] = df_complete_counties_agg['confirmed'].div(
        df_complete_counties_agg['pop_factor']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(4)

    return df_complete_counties_agg

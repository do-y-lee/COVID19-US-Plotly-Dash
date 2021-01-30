import pandas as pd
import numpy as np
from common.database import Database


class CovidCounties:
    @classmethod
    def agg_confirmed_counties(cls) -> pd.DataFrame:
        cursor = Database.read_all('confirmed_ts')
        df_confirmed_us = pd.DataFrame(list(cursor))

        if '_id' in df_confirmed_us.columns:
            df_confirmed_us.drop(['_id'], axis=1, inplace=True)

        # grab only the latest date confirmed case numbers - cumulative
        df1 = df_confirmed_us.loc[:, ['FIPS', 'Admin2', 'Province_State', 'Lat', 'Long_', 'Combined_Key']]

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

        # drop rows with Diamond Princess and Grand Princess and 80 out of state
        drop_list = ['88', '99', '80', '00']
        for fips in drop_list:
            df_confirmed_counties_agg = df_confirmed_counties_agg.drop(
                df_confirmed_counties_agg.index[df_confirmed_counties_agg['State FIPS'] == fips]).reset_index(drop=True)

        return df_confirmed_counties_agg

    @classmethod
    def agg_deaths_counties(cls) -> pd.DataFrame:
        cursor = Database.read_all('deaths_ts')
        df_deaths_us = pd.DataFrame(list(cursor))

        if '_id' in df_deaths_us.columns:
            df_deaths_us.drop(['_id'], axis=1, inplace=True)

        # create base df
        df_deaths_counties_stg = df_deaths_us.loc[:, ['FIPS', 'Admin2', 'Province_State', 'Population']]
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
                df_deaths_counties_agg.index[df_deaths_counties_agg['State FIPS'] == state_fips]
            ).reset_index(drop=True)

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

    @classmethod
    def agg_complete_counties(cls) -> pd.DataFrame:
        df_confirmed_counties_agg = cls.agg_confirmed_counties()
        df_deaths_counties_agg = cls.agg_deaths_counties()

        df_deaths_counties_agg = df_deaths_counties_agg.loc[:, ['State FIPS', 'FIPS', 'County', 'State/Territory',
                                                                'Population', 'deaths', 'Deaths']]
        join_columns = ['State FIPS', 'FIPS', 'County', 'State/Territory']
        df_complete_counties_agg = pd.merge(df_confirmed_counties_agg, df_deaths_counties_agg, how='left', on=join_columns)

        # create metrics: death rate by county, confirmed infection rate if pop available
        df_complete_counties_agg['Death Rate (%)'] = round(100 * df_complete_counties_agg['deaths'].div(
            df_complete_counties_agg['confirmed']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)), 4)

        df_complete_counties_agg['Est Pop'] = df_complete_counties_agg['Population'].fillna(0).astype(int).apply(lambda x: '{:,}'.format(x))

        df_complete_counties_agg['pop_factor'] = df_complete_counties_agg['Population'].fillna(0).div(1000)

        df_complete_counties_agg['Cases per 1000'] = df_complete_counties_agg['confirmed'].div(
            df_complete_counties_agg['pop_factor']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(4)

        return df_complete_counties_agg

    @classmethod
    def ts_confirmed_counties(cls) -> pd.DataFrame:
        cursor = Database.read_all('confirmed_ts')
        df_confirmed_us = pd.DataFrame(list(cursor))

        if '_id' in df_confirmed_us.columns:
            df_confirmed_us.drop(['_id'], axis=1, inplace=True)

        # create initial time series df
        df_conf_counties_ts = pd.concat(
            [df_confirmed_us.loc[:, ['FIPS', 'Province_State', 'Admin2']], df_confirmed_us.iloc[:, 11:]],
            axis=1
        )
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

        # transpose the TS models with pd.melt
        df_conf_counties_ts = pd.melt(df_conf_counties_ts,
                                      id_vars=['State FIPS', 'FIPS', 'State/Territory', 'County'],
                                      var_name='Date',
                                      value_name='Confirmed Cases')
        # convert Date into datetime
        df_conf_counties_ts['Date'] = pd.to_datetime(df_conf_counties_ts['Date'])

        # create County-State column
        df_conf_counties_ts['County-State'] = df_conf_counties_ts['County'] + ', ' + df_conf_counties_ts['State/Territory']

        return df_conf_counties_ts

    @classmethod
    def ts_deaths_counties(cls) -> pd.DataFrame:
        cursor = Database.read_all('deaths_ts')
        df_deaths_us = pd.DataFrame(list(cursor))

        if '_id' in df_deaths_us.columns:
            df_deaths_us.drop(['_id'], axis=1, inplace=True)

        # create new df
        df_deaths_counties_ts = pd.concat(
            [df_deaths_us.loc[:, ['FIPS', 'Province_State', 'Admin2', 'Population']], df_deaths_us.iloc[:, 12:]], axis=1)

        # rename columns
        df_deaths_counties_ts.rename(columns={'Province_State': 'State/Territory', 'Admin2': 'County'}, inplace=True)

        # modify FIPS column
        df_deaths_counties_ts['FIPS'] = df_deaths_counties_ts['FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(5))

        # transposing the models
        df_deaths_counties_ts = pd.melt(df_deaths_counties_ts,
                                        id_vars=['FIPS', 'State/Territory', 'County', 'Population'],
                                        var_name='Date',
                                        value_name='Deaths')
        # convert Date string into Date datetime
        df_deaths_counties_ts['Date'] = pd.to_datetime(df_deaths_counties_ts['Date'])

        return df_deaths_counties_ts

    @classmethod
    def ts_complete_counties(cls) -> pd.DataFrame:
        df_conf_counties_ts = cls.ts_confirmed_counties()
        df_deaths_counties_ts = cls.ts_deaths_counties()

        # select subset of columns
        df_deaths_counties_ts = df_deaths_counties_ts.loc[:, ['FIPS', 'State/Territory', 'County',
                                                              'Date', 'Population', 'Deaths']]
        join_columns = ['FIPS', 'State/Territory', 'County', 'Date']
        df_complete_counties_ts = pd.merge(df_conf_counties_ts, df_deaths_counties_ts, how='left', on=join_columns)

        # calculate 'Death Rate' by county using time series models
        df_complete_counties_ts['Death Rate (%)'] = 100 * df_complete_counties_ts['Deaths'].div(
            df_complete_counties_ts['Confirmed Cases']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(6)

        # create pop_factor (1000) to calculate 'Cases per 1000'
        df_complete_counties_ts['pop_factor'] = df_complete_counties_ts['Population'].fillna(0).div(1000)

        # calculate 'Cases per 1000' for time series
        df_complete_counties_ts['Cases per 1000'] = df_complete_counties_ts['Confirmed Cases'].div(
            df_complete_counties_ts['pop_factor']).replace((np.inf, -np.inf, np.nan), (0, 0, 0)).round(4)

        return df_complete_counties_ts

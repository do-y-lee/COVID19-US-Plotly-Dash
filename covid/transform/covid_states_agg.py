import pandas as pd
import numpy as np
from covid.transform.covid_counties_agg import complete_counties_agg
from covid.stats import states_stats


def complete_states_agg():
    """
    Cumulative confirmed cases and deaths by state
    :return: dataframe
    """
    # import and create base dataframes
    df_counties_agg = complete_counties_agg()
    df_states_stats = states_stats()

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

    # create formatted hover data for Plotly US map
    df_states_agg['Cases per 100k'] = df_states_agg['cc_per_100k'].apply(lambda x: '{:,}'.format(x))
    df_states_agg['Deaths per 100k'] = df_states_agg['d_per_100k'].apply(lambda x: '{:,}'.format(x))
    df_states_agg['Death Rate (%)'] = round(100 * df_states_agg['deaths'].div(df_states_agg['confirmed']).replace((np.nan, np.inf, -np.inf), (0, 0, 0)), 4)

    remove_list = ['American Samoa', 'Federated States of Micronesia', 'Palau',
                   'Guam', 'Virgin Islands', 'Marshall Islands', 'Northern Mariana Islands']
    df_states_agg = df_states_agg.drop(df_states_agg.index[df_states_agg['State/Territory'].isin(remove_list)])

    return df_states_agg

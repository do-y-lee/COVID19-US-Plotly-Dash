import pandas as pd


def states_stats():
    df = pd.read_csv('static/metadata/states_stats.csv')
    # convert 'State FIPS' into '00' string
    df['State FIPS'] = df['State FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(2))

    remove_list = ['American Samoa', 'Federated States of Micronesia',
                   'Palau', 'Guam', 'Virgin Islands', 'Marshall Islands',
                   'Northern Mariana Islands']

    df = df.drop(df.index[df['State/Territory'].isin(remove_list)])

    return df


def counties_stats():
    df = pd.read_csv('static/metadata/counties_stats.csv')
    # convert FIPS into string
    df['FIPS'] = df['FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(5))
    return df


def counties_population():
    df = pd.read_csv('static/metadata/counties_population.csv')
    return df

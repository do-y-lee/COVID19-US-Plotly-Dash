import pandas as pd
from common.database import Database


class Stats:
    @classmethod
    def states_stats(cls) -> pd.DataFrame:
        collection = 'states_stats'
        # returns a pymongo cursor and pandas to convert to df
        cursor = Database.read_all(collection)
        df = pd.DataFrame(list(cursor))

        if '_id' in df.columns:
            df.drop(['_id'], axis=1, inplace=True)

        # convert 'State FIPS' into '00' string
        df['State FIPS'] = df['State FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(2))

        remove_list = ['American Samoa', 'Federated States of Micronesia',
                       'Palau', 'Guam', 'Virgin Islands', 'Marshall Islands',
                       'Northern Mariana Islands']
        df = df.drop(df.index[df['State/Territory'].isin(remove_list)])

        return df

    @classmethod
    def counties_stats(cls) -> pd.DataFrame:
        collection = 'counties_stats'
        cursor = Database.read_all(collection)
        df = pd.DataFrame(list(cursor))

        if '_id' in df.columns:
            df.drop(['_id'], axis=1, inplace=True)

        # convert FIPS into string
        df['FIPS'] = df['FIPS'].fillna(0).astype(int).apply(lambda x: str(x).zfill(5))

        return df

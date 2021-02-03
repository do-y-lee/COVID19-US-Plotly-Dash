import os
import pandas as pd
from common.database import Database

# states and counties stats csv files
files = {'counties_stats.csv': 'counties_stats',
         'states_stats.csv': 'states_stats'}


# one-time run to insert states and counties stats into Mongodb collections (counties_stats & states_stats)
def stats_csv_to_mongo():
    path = os.path.join(os.getcwd(), 'data/stats')
    print(path)
    for file, collection in files.items():
        Database.delete(collection)

        data = pd.read_csv(os.path.join(path, file))
        data_dict = data.to_dict('records')

        Database.insert(collection, data_dict)


if __name__ == '__main__':
    stats_csv_to_mongo()

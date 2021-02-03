import os
import requests
import logging
import pandas as pd
from common.database import Database

files = {'time_series_covid19_confirmed_US.csv': 'confirmed_ts',
         'time_series_covid19_deaths_US.csv': 'deaths_ts'}


# Grab John Hopkins' time-series covid files from their public Github repo
def grab_covid_csv():
    raw_url = 'https://raw.githubusercontent.com'
    raw_path = 'CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'

    try:
        for file in files:
            url = os.path.join(raw_url, raw_path, file)
            data = requests.get(url)
            csv_data = data.text
            local_file = os.path.join(os.getcwd(), 'data/covid', file)
            # print(local_file)

            with open(local_file, 'w') as f:
                f.write(csv_data)
                f.close()

    except Exception as e:
        logging.error('Exception error.', exc_info=e)


# Take JH downloaded csv files and insert into MongoDB
def insert_csv_to_mongo():
    file_path = os.path.join(os.getcwd(), 'data/covid')

    for file, collection in files.items():
        # delete all documents in the collection
        Database.delete(collection)

        # read csv files saved locally and convert to dict using 'records' parameter
        data = pd.read_csv(os.path.join(file_path, file))
        data_dict = data.to_dict('records')

        # insert models dict into collection
        Database.insert(collection, data_dict)


if __name__ == '__main__':
    grab_covid_csv()
    insert_csv_to_mongo()

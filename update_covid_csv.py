import os
import requests


def update_covid_csv_files():
    raw_url = 'https://raw.githubusercontent.com'
    raw_path = 'CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'
    files = ['time_series_covid19_confirmed_US.csv', 'time_series_covid19_deaths_US.csv']

    try:
        for file in files:
            url = os.path.join(raw_url, raw_path, file)
            data = requests.get(url)
            csv_data = data.text

            local_file = os.path.join(os.getcwd(), 'static/data', file)
            print(local_file)
            with open(local_file, 'w') as f:
                f.write(csv_data)
    except:
        pass


if __name__ == '__main__':
    update_covid_csv_files()


# COVID-19 United States Tracker

> Aggregating and monitoring COVID-19 metrics at the national, state and county level.


---

## Description

- The Plotly Dash application tracks key metrics related COVID-19 in the United States. 
- Metrics are displayed through mapbox heatmaps, time series, as well as aggregated values.
- Metrics cover states and counties in the United States.

## Key Metrics

- Confirmed Cases
- Deaths 
- Cases per 100k and Cases per 1000
- Deaths per 100k
- Death Rate (Deaths/Confirmed Cases per specified area)
- Population by county, state, and USA

## Tech Stack

- Python
- Plotly Dash / Flask
- Heroku: Dev Deployment
- Digital Ocean: Prod Deployment
  - Droplet Ubuntu 18.04
  - Nginx
  - uWSGI
  - MongoDB
    


## Data Sources

- [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)
- [U.S. Census](https://www.census.gov/)


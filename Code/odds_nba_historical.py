import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time
from scipy.stats import zscore
from scipy.stats import norm
import pandas as pd
import glob
import argparse
import os

#######################################################################
parser = argparse.ArgumentParser(description='Sample V4')
parser.add_argument('--api-key', type=str, default='')
args = parser.parse_args()

API_KEY = args.api_key or '8f6ac42e4584c9bacffc9e1a0fec95a3'

#######################################################################
# Sport key
# https://the-odds-api.com/sports-odds-data/sports-apis.html

#SPORT = 'upcoming'
SPORT = 'basketball_nba'

# Bookmaker regions
# uk | us | us2 | eu | au
REGIONS = 'us'

# Odds markets
# h2h | spreads | totals
MARKETS = 'h2h,spreads,totals'

PROP_MARKETS = ['player_points', 
                'player_assists', 
                'player_rebounds', 
                'player_threes',
                'player_points_rebounds_assists',
                'player_points_rebounds',
                'player_points_assists',
                'player_rebounds_assists']

# Odds format
# decimal | american
ODDS_FORMAT = 'american'

# Date format
DATE_FORMAT = 'iso'

"""
dates = ['2024-02-29T12:00:00Z',
         '2024-02-28T12:00:00Z',
         '2024-02-27T12:00:00Z',
         '2024-02-26T12:00:00Z',
         '2024-02-25T12:00:00Z',
         '2024-02-24T12:00:00Z',
         '2024-02-23T12:00:00Z',
         '2024-02-22T12:00:00Z',
         '2024-02-21T12:00:00Z',
         '2024-02-20T12:00:00Z',
         '2024-02-19T12:00:00Z',
         '2024-02-18T12:00:00Z',
         '2024-02-17T12:00:00Z',
         '2024-02-16T12:00:00Z',
         '2024-02-15T12:00:00Z',
         '2024-02-14T12:00:00Z',
         '2024-02-13T12:00:00Z',
         '2024-02-12T12:00:00Z',
         '2024-02-11T12:00:00Z', 
         '2024-02-10T12:00:00Z',
         '2024-02-09T12:00:00Z']
"""

dates = ['2024-02-29T12:00:00Z']
#######################################################################

responses_date = []
flattened_data_date_list = []

for date in dates:
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/historical/sports/{SPORT}/events', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
        'date': date
    })
    responses_date.append(odds_response.json())

    flattened_date_list = pd.json_normalize(responses_date, 'data', errors='ignore')
    flattened_data_date_list.append(flattened_date_list)

flattened_date_prop = pd.concat(flattened_data_date_list)

flattened_date_prop.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\stats_full_data\test.csv', header=True)

df_id = flattened_date_prop[['id','commence_time']]

#df_id.to_csv(r'G:\My Drive\Code\EV Bets\test2.csv', header=True)

######################################

responses = []
flattened_data_prop_list = []


for market in PROP_MARKETS:
    for index, row in df_id.iterrows():
        EVENT_ID = row['id']
        event_response = requests.get(f'https://api.the-odds-api.com/v4/historical/sports/{SPORT}/events/{EVENT_ID}/odds', params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': market,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
            'date': row['commence_time']
        })
        responses.append(event_response.json())
        flattened_data_prop = pd.json_normalize(responses, ['data', 'bookmakers', 'markets', 'outcomes'], 
                                        ['timestamp',
                                         ['data', 'id'],
                                         ['data', 'home_team'],
                                         ['data', 'away_team'], 
                                         ['data', 'bookmakers', 'title'],
                                         ['data', 'bookmakers', 'markets', 'key']], 
                                        record_prefix='outcomes_', errors='ignore')
        
        flattened_data_prop_list.append(flattened_data_prop)

flattened_data_prop = pd.concat(flattened_data_prop_list)

if event_response.status_code != 200:
    print(f'Failed to get odds: status_code {event_response.status_code}, response body {event_response.text}')

else:
    event_response_json = event_response.json()
    print('Remaining requests', event_response.headers['x-requests-remaining'])
    print('Used requests', event_response.headers['x-requests-used'])

flattened_data_prop = flattened_data_prop.drop_duplicates()


#######################################################################

#Export test to desktop
#flattened_data_prop.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\prop_data\data_points_historical.csv', header=True)

current_directory = os.getcwd()
filename_flattened_data_prop = 'data_points_historical.csv'
full_path_flattened_data_prop = os.path.join(current_directory, 'data', 'prop_data', filename_flattened_data_prop)
flattened_data_prop.to_csv(full_path_flattened_data_prop , header=True)
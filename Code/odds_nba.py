import argparse
import requests
import pandas as pd
import datetime
from datetime import datetime
import time
import io
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
REGIONS = 'us'

# Odds markets
MARKETS = 'h2h,spreads,totals'

#Prop Market keys
PROP_MARKETS = ['player_points', 
                'player_assists', 
                'player_rebounds', 
                'player_threes',
                'player_points_rebounds_assists',
                'player_points_rebounds',
                'player_points_assists',
                'player_rebounds_assists']

# Odds format
ODDS_FORMAT = 'american'

# Date format
DATE_FORMAT = 'iso'

#######################################################################
# Get the list of game IDS from the previous day

odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
    'api_key': API_KEY,
    'regions': REGIONS,
    'markets': MARKETS,
    'oddsFormat': ODDS_FORMAT,
    'dateFormat': DATE_FORMAT,
})

#if odds_response.status_code != 200:
#    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

#else:
odds_json = odds_response.json()
#print('Number of events:', len(odds_json))
#print(odds_json)

# Check the usage quota
print('Remaining requests', odds_response.headers['x-requests-remaining'])
print('Used requests', odds_response.headers['x-requests-used'])


df_id = pd.json_normalize(odds_json)
df_id = df_id[['id']]

#######################################################################
# Event response for player probs. Uses game ID list

responses = []
flattened_data_prop_list = []

for market in PROP_MARKETS:
    EVENT_IDS = df_id['id'].tolist()
    for EVENT_ID in EVENT_IDS:
        event_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/events/{EVENT_ID}/odds', params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': market,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        })
        responses.append(event_response.json())

        flattened_data_prop = pd.json_normalize(responses, ['bookmakers', 'markets', 'outcomes'], 
                                                ['id', 
                                                 'sport_key', 
                                                 'sport_title', 
                                                 'commence_time', 
                                                 'home_team', 
                                                 'away_team', 
                                                 ['bookmakers', 'key'], 
                                                 ['bookmakers', 'title'], 
                                                 ['bookmakers', 'last_update'],
                                                 ['bookmakers', 'markets', 'key'], 
                                                 ['bookmakers', 'markets', 'last_update']], 
                                                record_prefix='outcomes_', errors='ignore')
        flattened_data_prop_list.append(flattened_data_prop)
    print('Prop Market ', market, ' Complete')

#Merge all files from list into one dataframe
flattened_data_prop = pd.concat(flattened_data_prop_list)

if event_response.status_code != 200:
    print(f'Failed to get odds: status_code {event_response.status_code}, response body {event_response.text}')

else:
    event_response_json = event_response.json()
    print('Remaining requests', event_response.headers['x-requests-remaining'])
    print('Used requests', event_response.headers['x-requests-used'])

#Dedup just in case the pull did the same days
flattened_data_prop = flattened_data_prop.drop_duplicates()

#######################################################################
#Outputs

today_date = datetime.today().date()
today_date_str = today_date.strftime('%Y-%m-%d')
current_directory = os.getcwd()

#Exports
filename_data_prop = 'data_points_'+today_date_str+'.csv'
full_path_data_prop = os.path.join(current_directory, 'data', 'prop_data', filename_data_prop)
flattened_data_prop.to_csv(full_path_data_prop , header=True)

print('Odds Pull Complete')


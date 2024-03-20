import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time
from scipy.stats import zscore
from scipy.stats import norm
import pandas as pd
import glob
import os
from dotenv import load_dotenv, dotenv_values

#######################################################################
#API pull Data
#https://rapidapi.com/api-sports/api/api-nba

load_dotenv()

headers = {
	"X-RapidAPI-Key": os.getenv("stats_api_key"),
	"X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}
api = "https://api-nba-v1.p.rapidapi.com/"

#######################################################################
#Functions

#Pull game data IDS
def pullGames(date):
    url = api + "games"
    querystring = {"date":date}
    local_header = headers
    response = requests.get(url, headers=local_header, params=querystring)
    return response

#Pull game stats
def pullGameStats(gameID):
    url = api + "players/statistics"
    querystring = {"game":gameID}
    local_header = headers
    response = requests.get(url, headers=local_header, params=querystring)
    return response

#Time frame for yesterday
def get_last_day():
    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(0,5)]
    return date_list

#Deviation Calculation
def calculate_deviation(df, stat):
    df[stat+'_deviation'] = (df[stat] - df[stat+'_avg']) ** 2
    return df

#Date
today_date = datetime.today().date()
today_date_str = today_date.strftime('%Y-%m-%d')

current_directory = os.getcwd()

#######################################################################
#Date Stuff
dates = get_last_day()
dates = [date.strftime("%Y-%m-%d") for date in dates]
dates = pd.DataFrame(dates, columns=['Date'])
dates = dates['Date'].tolist()

#######################################################################
#Pull Game list. Loop through all days

games_list = []

for date in dates:
    games = pullGames(date)
    games_json = games.json()

    for i in games_json['response']:
        row = {
            "id": i['id'],
            "date": i['date']['start'],   #games_json['parameters']['date']
            "home_team": i['teams']['home']['name'],
            "away_team": i['teams']['visitors']['name']
        }
        games_list.append(row)


EVENT_IDS = [game['id'] for game in games_list]

games_list_df = pd.DataFrame(games_list)

full_path_games_list_df = os.path.join(current_directory, 'data','full_game_list', 'game_list_'+today_date_str+'.csv')
games_list_df.to_csv(full_path_games_list_df, header=True)

#######################################################################
#Pull data from each game

data_stats = []

for EVENT_ID in EVENT_IDS:
    stats = pullGameStats(EVENT_ID)
    stats_list = stats.json()
    
    for i in stats_list['response']:
        row = {
            "player_id": i['player']['id'],
            "firstname": i['player']['firstname'],
            "lastname": i['player']['lastname'],
            "team": i['team']['name'],
            "game_id": i['game']['id'],
            "points": i['points'],
            "position": i['pos'],
            "minutes": i['min'],
            "fgm": i['fgm'],
            "fga": i['fga'],
            "fgp": i['fgp'],
            "ftm": i['ftm'],
            "fta": i['fta'],
            "ftp": i['ftp'],
            "tpm": i['tpm'],
            "tpa": i['tpa'],
            "tpp": i['tpp'],
            "offReb": i['offReb'],
            "defReb": i['defReb'],
            "totReb": i['totReb'],
            "assists": i['assists'],
            "pFouls": i['pFouls'],
            "steals": i['steals'],
            "turnovers": i['turnovers'],
            "blocks": i['blocks'],
            "plusMinus": i['plusMinus']
        }
        data_stats.append(row)
    print('Pulling Stats for Game ID:', i['game']['id'])

#######################################################################
#Data Cleaning and column creation

data_stats_df = pd.DataFrame(data_stats)
data_stats_df['First Last Name'] = data_stats_df['firstname'] + ' ' + data_stats_df['lastname']

#Add in more stats
data_stats_df['Points_Rebounds_Assist'] = data_stats_df['points'] + data_stats_df['totReb'] + data_stats_df['assists']
data_stats_df['Points_Rebounds'] = data_stats_df['points'] + data_stats_df['totReb']
data_stats_df['Points_Assist'] = data_stats_df['points']+ data_stats_df['assists']
data_stats_df['Rebounds_Assist'] = data_stats_df['totReb'] + data_stats_df['assists']

#data_stats_df['date'] = pd.to_datetime(data_stats_df['date']).dt.strftime('%m/%d/%Y %I:%M:%S %p')

# Get the file paths
data_stats_df = pd.merge(data_stats_df, games_list_df, how='left', left_on='game_id', right_on='id')

# Convert date strings to datetime
data_stats_df['date'] = pd.to_datetime(data_stats_df['date']).dt.tz_convert(None)
data_stats_df['date'] = data_stats_df['date'].dt.strftime('%-m/%-d/%Y %I:%M:%S %p')

#Import Old data
file_paths = glob.glob(os.path.join(current_directory,'data', 'stats_full_data', '*.csv'))

# Read the CSV files into a DataFrame
df = pd.concat((pd.read_csv(file) for file in file_paths), ignore_index=True)

#Export current day data before concat
filename_data_stats_df = 'data_stats_'+today_date_str+'.csv'
full_path_data_stats_df = os.path.join(current_directory, 'data', 'stats_full_data', filename_data_stats_df)
data_stats_df.to_csv(full_path_data_stats_df, header=True)

#Concat data
data_stats_df = pd.concat([data_stats_df, df], ignore_index=True)

#######################################################################
#Team Fix

file_path_team_fix = os.path.join(current_directory, 'lookups', 'player_team_fix.csv')
team_fix = pd.read_csv(file_path_team_fix)

name_team_dict = dict(zip(team_fix['Name'], team_fix['Team']))
data_stats_df['team'] = data_stats_df['First Last Name'].map(name_team_dict).fillna(data_stats_df['team'])

#######################################################################
#Calculate average by player
average_points = data_stats_df.groupby('player_id').agg({
    'points': 'mean',
    'totReb': 'mean',
    'assists': 'mean',
    'tpm': 'mean',
    'Points_Rebounds_Assist': 'mean',
    'Points_Rebounds': 'mean',
    'Points_Assist': 'mean',
    'Rebounds_Assist': 'mean'
})

#Merge back onto original and calculation deviation
average_points.columns = average_points.columns.map(lambda x: x + '_avg')
data_stats_df = data_stats_df.merge(average_points, on='player_id', how='left')

stats_for_variance = ['points', 'totReb', 'assists','tpm','Points_Rebounds_Assist', 'Points_Rebounds', 'Points_Assist', 'Rebounds_Assist']

for stat in stats_for_variance:
    data_stats_df = calculate_deviation(data_stats_df, stat)

#######################################################################
#Filters and Cleaning

#Filter out players
data_stats_df['minutes'] = pd.to_numeric(data_stats_df['minutes'], errors='coerce')
data_stats_df['minutes'] = data_stats_df['minutes'].fillna(0).astype(int)
data_stats_df = data_stats_df[data_stats_df['minutes'] >= 5]

#######################################################################
# Subtract 6 hours because the time zone is GMT and some of the night games leak over to the next day
#print(data_stats_df['date'].unique())

# Convert date strings using the format "%Y-%m-%d %H:%M:%S"
data_stats_df['date'] = pd.to_datetime(data_stats_df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Find any NaT values
nat_rows = data_stats_df['date'].isna()

# Convert any remaining date strings using the format "%m/%d/%Y %H:%M"
data_stats_df.loc[nat_rows, 'date'] = pd.to_datetime(data_stats_df.loc[nat_rows, 'date'], format='%m/%d/%Y %H:%M', errors='coerce')

# Subtract 6 hours from each datetime
data_stats_df['date'] = data_stats_df['date'] - pd.Timedelta(hours=6)

# Convert datetime to the desired format
data_stats_df['date'] = data_stats_df['date'].dt.strftime('%-m/%-d/%Y %I:%M:%S %p')


#######################################################################

#Drop duplicates in case of overlap
data_stats_df = data_stats_df.drop_duplicates(subset=['player_id', 'game_id'])

# Sort by 'player_id' and 'date'
data_stats_df = data_stats_df.sort_values(['player_id', 'date'])

# Keep only the last 10 rows for each 'player_id'
data_stats_df = data_stats_df.groupby('player_id').tail(10)

#For last 10 games stats charts
filename_last10games_single = 'data_stats_last_10.csv'
full_path_last10games_single = os.path.join(current_directory, 'data', 'stats_data_last10', filename_last10games_single)
data_stats_df.to_csv(full_path_last10games_single, header=True)


#######################################################################
#Group by players and sum stats

columns_to_sum = ['points', 
                  'minutes', 
                  'fgm', 
                  'fga', 
                  'fgp', 
                  'ftm', 
                  'fta', 
                  'ftp', 
                  'tpm', 
                  'tpa', 
                  'tpp', 
                  'offReb', 
                  'defReb', 
                  'totReb', 
                  'assists', 
                  'pFouls', 
                  'steals', 
                  'turnovers', 
                  'blocks', 
                  'plusMinus',
                  'Points_Rebounds_Assist', 
                  'Points_Rebounds', 
                  'Points_Assist', 
                  'Rebounds_Assist',
                  'points_deviation', 
                  'totReb_deviation', 
                  'assists_deviation',
                  'tpm_deviation', 
                  'Points_Rebounds_Assist_deviation', 
                  'Points_Rebounds_deviation', 
                  'Points_Assist_deviation', 
                  'Rebounds_Assist_deviation']

group_columns = ['First Last Name', 'team', 'position']

#Convert to numeric
data_stats_df[columns_to_sum] = data_stats_df[columns_to_sum].apply(pd.to_numeric, errors='coerce')

#Get all coluns
all_columns = group_columns + columns_to_sum

#Group by and sum
grouped_df = data_stats_df[all_columns].groupby(group_columns).sum().reset_index()
grouped_df['count'] = data_stats_df[group_columns].groupby(group_columns).size().reset_index(name='count')['count']

#######################################################################
#OUTPUTS for merging stats onto odds data for calcs

filename_last10games = 'data_stats_last10games_'+today_date_str+'.csv'
full_path_last10games = os.path.join(current_directory, 'data', 'stats_data_group', filename_last10games)
grouped_df.to_csv(full_path_last10games, header=True)
print('Stat Pull Complete')


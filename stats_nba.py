import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time
from scipy.stats import zscore
from scipy.stats import norm
import pandas as pd
import glob

#######################################################################
#API pull Data
#https://rapidapi.com/api-sports/api/api-nba
headers = {
	"X-RapidAPI-Key": "7f15289082msh2b80f8151be1e74p16fba4jsnff9ea5c99f8d",
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
    if response.status_code != 200:
        print(f'Failed to get odds: status_code {response.status_code}, response body {response.text}')
    else:
        print('Stat pull Success')
    return response

#Time frame for yesterday
def get_last_day():
    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(0,2)]
    return date_list

#Deviation Calculation
def calculate_deviation(df, stat):
    df[stat+'_deviation'] = (df[stat] - df[stat+'_avg']) ** 2
    return df

#Date
today_date = datetime.today().date()
today_date_str = today_date.strftime('%Y-%m-%d')

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
            "date": i['date']['start']   #games_json['parameters']['date']
        }
        games_list.append(row)


EVENT_IDS = [game['id'] for game in games_list]

games_list_df = pd.DataFrame(games_list)

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

#######################################################################
#Data Cleaning and column creation

data_stats_df = pd.DataFrame(data_stats)
data_stats_df['First Last Name'] = data_stats_df['firstname'] + ' ' + data_stats_df['lastname']

#Add in more stats
data_stats_df['Points_Rebounds_Assist'] = data_stats_df['points'] + data_stats_df['totReb'] + data_stats_df['assists']
data_stats_df['Points_Rebounds'] = data_stats_df['points'] + data_stats_df['totReb']
data_stats_df['Points_Assist'] = data_stats_df['points']+ data_stats_df['assists']
data_stats_df['Rebounds_Assist'] = data_stats_df['totReb'] + data_stats_df['assists']


# Get the file paths
data_stats_df = pd.merge(data_stats_df, games_list_df, how='left', left_on='game_id', right_on='id')
#data_stats_df['date'] = pd.to_datetime(data_stats_df['date'])
data_stats_df['date'] = pd.to_datetime(data_stats_df['date']).dt.strftime('%m/%d/%Y %I:%M:%S %p')
#data_stats_df['date'] = data_stats_df['date'] - pd.Timedelta(hours=6)

#Import Old data
file_paths = glob.glob('C:\\Users\\Brian\\Main Folder\\EV Bets\\stats_full_data\\*.csv')

# Read the CSV files into a DataFrame
df = pd.concat((pd.read_csv(file) for file in file_paths), ignore_index=True)

#Export current day data before concat
data_stats_df.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\stats_full_data\data_stats_'+today_date_str+'.csv', header=True)

#Concat data
data_stats_df = pd.concat([data_stats_df, df], ignore_index=True)

#######################################################################
#Team Fix
team_fix = pd.read_csv(r'C:\Users\Brian\Main Folder\EV Bets\lookups\player_team_fix.csv')
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
#Filter out players
data_stats_df['minutes'] = data_stats_df['minutes'].astype(int)
data_stats_df = data_stats_df[data_stats_df['minutes'] >= 5]

# Subtract 6 hours because randomly the data is set at gmt
data_stats_df['date'] = pd.to_datetime(data_stats_df['date'], format='%m/%d/%Y %I:%M:%S %p')- pd.Timedelta(hours=6)
data_stats_df['date'] = data_stats_df['date'].dt.date

#Drop duplicates in case of overlap
data_stats_df = data_stats_df.drop_duplicates(subset=['player_id', 'game_id'])

# Sort by 'player_id' and 'date'
data_stats_df = data_stats_df.sort_values(['player_id', 'date'])

# Keep only the last 10 rows for each 'player_id'
data_stats_df = data_stats_df.groupby('player_id').tail(10)

#For last 10 games stats charts
data_stats_df.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\stats_data_last10\data_stats_last_10.csv', header=True)

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

data_stats_df[columns_to_sum] = data_stats_df[columns_to_sum].apply(pd.to_numeric, errors='coerce')

all_columns = group_columns + columns_to_sum

grouped_df = data_stats_df[all_columns].groupby(group_columns).sum().reset_index()
grouped_df['count'] = data_stats_df[group_columns].groupby(group_columns).size().reset_index(name='count')['count']


#######################################################################
#OUTPUTS for merging stats onto odds data for calcs
grouped_df.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\stats_data_group\data_stats_last10games_'+today_date_str+'.csv', header=True)

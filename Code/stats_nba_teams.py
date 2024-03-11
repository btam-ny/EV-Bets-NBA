import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time
from scipy.stats import zscore
from scipy.stats import norm
import glob
import os
from dotenv import load_dotenv, dotenv_values

#######################################################################
#API Info
#https://rapidapi.com/api-sports/api/api-nba
load_dotenv()

headers = {
	"X-RapidAPI-Key": os.getenv("stats_api_key"),
	"X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}
api = "https://api-nba-v1.p.rapidapi.com/"


#######################################################################
#Functions and Variations

def pullGames(date):
    url = api + "games"
    querystring = {"date":date}
    local_header = headers
    response = requests.get(url, headers=local_header, params=querystring)
    return response

def pullTeamStats(gameID):
    url = api + "games/statistics"
    querystring = {"id":gameID}
    local_header = headers
    response = requests.get(url, headers=local_header, params=querystring)
    return response

def get_last_game():
    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(0,1)]
    return date_list

def switch_team_name(group):
    group['team name'] = group['team name'].iloc[::-1].values
    return group

def group_and_sum(df, columns_to_sum, group_columns):
    df[columns_to_sum] = df[columns_to_sum].apply(pd.to_numeric, errors='coerce')
    all_columns = group_columns + columns_to_sum
    grouped_df = df[all_columns].groupby(group_columns).sum().reset_index()
    grouped_df['count'] = df[group_columns].groupby(group_columns).size().reset_index(name='count')['count']
    return grouped_df

def calculate_avg(df,stat,games):
    return df[stat] / df[games]

today_date = datetime.today().date()
today_date_str = today_date.strftime('%Y-%m-%d')

current_directory = os.getcwd()

#######################################################################

dates = get_last_game()
dates = [date.strftime("%Y-%m-%d") for date in dates]
dates = pd.DataFrame(dates, columns=['Date'])
dates = dates['Date'].tolist()

#######################################################################
games_list = []

for date in dates:
    games = pullGames(date)
    games_json = games.json()

    for i in games_json['response']:
        row = {
            "id": i['id'],
            "date": games_json['parameters']['date']
        }
        games_list.append(row)

EVENT_IDS = [game['id'] for game in games_list]

games_list_df = pd.DataFrame(games_list)

#######################################################################
#Import data from API

data_stats = []

for EVENT_ID in EVENT_IDS:
    stats = pullTeamStats(EVENT_ID)
    stats_list = stats.json()
    
    for i in stats_list['response']:
        for j in i['statistics']:
            row = {
                "game_id": stats_list['parameters']['id'],
                "team name": i['team']['name'],
                "team name": i['team']['nickname'],
                "points": j['points'],
                "assists": j['assists'],
                "offReb": j['offReb'],
                "defReb": j['defReb'],
                "totReb": j['totReb'],
                "steals": j['steals'],
                "turnovers": j['turnovers'],
                "blocks": j['blocks'],
                "tpm": j['tpm'],
                "tpa": j['tpa'],
                "plusMinus": j['plusMinus'],
                "fastBreakPoints": j['fastBreakPoints'],
                "pointsInPaint": j['pointsInPaint'],
                "biggestLead": j['biggestLead'],
                "secondChancePoints": j['secondChancePoints'],
                "pointsOffTurnovers": j['pointsOffTurnovers'],
                "longestRun": j['longestRun'],
                "fgm": j['fgm'],
                "fga": j['fga'],
                "ftm": j['ftm'],
                "fta": j['fta'],
                "pfouls": j['pFouls']
            }
            data_stats.append(row)
    print('Event ID: ', EVENT_ID, ' Complete')

#Turn Data stats into a df
data_stats_df = pd.DataFrame(data_stats)

#Merge Stats with game list
data_stats_df['game_id'] = data_stats_df['game_id'].astype(int)
data_stats_df = pd.merge(data_stats_df, games_list_df, how='left', left_on='game_id', right_on='id')

#######################################################################
#Historical and Current Merge

#Load in historical data. Do this before loading in path so current is not in it
file_paths = glob.glob(os.path.join(current_directory,'data', 'team_defense_full_data', '*.csv'))
df = pd.concat((pd.read_csv(file) for file in file_paths), ignore_index=True)

#Export todays data
filename_defense_full_stats = 'team_data_defense_full_'+today_date_str+'.csv'
full_path_data_stats = os.path.join(current_directory,'data', 'team_defense_full_data', filename_defense_full_stats)
data_stats_df.to_csv(full_path_data_stats, header=True)

#Concat Historical and current data
data_stats_df = pd.concat([data_stats_df, df], ignore_index=True)

#Flip game ids for defensive stats and drop dupcliates
data_stats_df = data_stats_df.groupby('game_id').apply(switch_team_name)
data_stats_df = data_stats_df.drop_duplicates()

# Keep only last 10 games
data_stats_df = data_stats_df.sort_values(['team name', 'date'])
data_stats_df = data_stats_df.groupby('team name').tail(10)

#######################################################################
#Group teams in pivot

columns_to_sum = ['points', 'assists', 'offReb', 'defReb', 'totReb', 'steals', 'turnovers', 'blocks', 'tpm', 'tpa', 'plusMinus', 'fastBreakPoints', 'pointsInPaint', 'biggestLead', 'secondChancePoints', 'pointsOffTurnovers', 'longestRun', 'fgm', 'fga', 'ftm', 'fta', 'pfouls']
group_columns = ['team name']

#Group by team
defense_df = group_and_sum(data_stats_df, columns_to_sum, group_columns)

#######################################################################
#Add combo stats and possessions
defense_df['Points_Rebounds_Assist'] = defense_df['points'] + defense_df['totReb'] + defense_df['assists']
defense_df['Points_Rebounds'] = defense_df['points'] + defense_df['totReb']
defense_df['Points_Assist'] = defense_df['points']+ defense_df['assists']
defense_df['Rebounds_Assist'] = defense_df['totReb'] + defense_df['assists']
defense_df['Possessions'] = defense_df['fga'] + (defense_df['fta'] * .475) - defense_df['offReb'] + defense_df['turnovers']

#######################################################################
#Calculate stat efficiency
defensive_eff_stats = ['points','assists','tpm','totReb','Points_Rebounds_Assist','Points_Rebounds','Points_Assist','Rebounds_Assist']

#Calculate teams stat per possession
for stat in defensive_eff_stats:
    defense_df[stat+'_pp'] = calculate_avg(defense_df,stat,'Possessions')

#Calculate league stat per possession
for stat in defensive_eff_stats:
    defense_df[stat+'_league_pp'] = defense_df[stat].sum() / defense_df['Possessions'].sum()

#Calculate efficiency. Team effiency / league effiency
for stat in defensive_eff_stats:
    defense_df[stat+'_eff'] = defense_df[stat+'_pp'] / defense_df[stat+'_league_pp']

#Drop columns
keep_cols = ['team name','points_eff','assists_eff','tpm_eff','totReb_eff','Points_Rebounds_Assist_eff','Points_Rebounds_eff','Points_Assist_eff','Rebounds_Assist_eff']
defense_df = defense_df[keep_cols]

#######################################################################
#Export

filename_defense_df_10 = 'team_data_defense_last10_'+today_date_str+'.csv'
full_path_defense_df = os.path.join(current_directory,'data','team_defense_data', filename_defense_df_10)
defense_df.to_csv(full_path_defense_df , header=True)
print('Team Pull Complete')


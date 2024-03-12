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

#Time frame for yesterday
def get_last_day():
    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(0,50)]
    return date_list

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

full_path_games_list_df = os.path.join(current_directory, 'data','full_game_list', 'game_list.csv')
games_list_df.to_csv(full_path_games_list_df, header=True)
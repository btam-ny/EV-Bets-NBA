import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
import requests
import datetime
from datetime import datetime
from scipy.stats import zscore
from scipy.stats import norm
import numpy as np

#######################################################################
#Data Load
today_date = datetime.today().date()
today_date_str = today_date.strftime('%Y-%m-%d')

#Load in prop odds, last 10 stats and defensive ratings
prop_odds = pd.read_csv(r'C:\Users\Brian\Main Folder\EV Bets\prop_data\data_points_'+ today_date_str +'.csv')
last_10_stats = pd.read_csv(r'C:\Users\Brian\Main Folder\EV Bets\stats_data_group\data_stats_last10games_'+today_date_str+'.csv')
defensive_rating = pd.read_csv(r'C:\Users\Brian\Main Folder\EV Bets\team_defense_data\team_data_defense_last10_'+today_date_str+'.csv')

#Load in name/team fixes
name_fix = pd.read_csv(r'C:\Users\Brian\Main Folder\EV Bets\lookups\name_fix.csv')
team_name_fix = pd.read_csv(r'C:\Users\Brian\Main Folder\EV Bets\lookups\team_name_fix.csv')

#######################################################################
#Variables
vig = 1.06775067750678 #Draft kings vig
bookmaker_filter = ['FanDuel', 'BetMGM', 'Caesars','DraftKings']
stats_to_pull=['points','totReb','assists','tpm','Points_Rebounds_Assist','Points_Rebounds','Points_Assist','Rebounds_Assist']

#Columns to keep on main output
columns_to_keep = ['outcomes_description',
                   'outcomes_name',
                   'outcomes_price',
                   'outcomes_point',
                   'EV Percentage',
                   'bookmakers.title',
                   'bookmakers.markets.key',
                   'team',
                   'Outcome Last 30 Avg',
                   'Outcome Last 30 Avg Adjusted',
                   'True Odds', 
                   'Percentage Hit',
                   'opposing team',
                   'Defensive Rating Adjustment',
                   'Outcome Last 30 STD',
                   'outcomes_point_adj']

#######################################################################
#Functions

#Calculates percentage odds from american odds
def calculate_value(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

#Standardize data for normal distribution
def standardize(mean,value, std_dev):
    return (value - mean) / std_dev

#Calculate normal distribution
def calculate_norm_dist(value):
    return norm.cdf(value, 0, 1)

#Calculate average
def calculate_avg(df,stat,games):
    return df[stat] / df[games]

#Calculate standard deviation
def calculate_std(df,stat,games):
    return (df[stat] / df[games]) ** 0.5

#Calculate EV, Percentage Hit
def process_data(df,stat,std_dev):
    df['Odds with Vig'] = df['outcomes_price'].apply(calculate_value)
    df['True Odds'] = df['Odds with Vig'] / vig
    df['Standardize'] = standardize(df['outcomes_point_adj'], df[stat], df[std_dev])
    df['std_adjustment'] = df['outcomes_name'].apply(lambda x: -1 if 'Under' in x else 1)
    df['Actual STD'] = df['std_adjustment'] * df['Standardize']
    df['Percentage Hit'] = calculate_norm_dist(df['Actual STD'])
    df['EV Percentage'] = (df['Percentage Hit']-df['True Odds'])/df['Percentage Hit']
    return df

#######################################################################
#Cleaning Data

#Fixing Names
name_dict = dict(zip(name_fix['Original Name'], name_fix['Fixed Name']))
prop_odds['outcomes_description'] = prop_odds['outcomes_description'].map(name_dict).fillna(prop_odds['outcomes_description'])

#Adjusting outcomes to be whole numbers for over/unders
prop_odds['outcomes_point_adj'] = prop_odds.apply(lambda row: row['outcomes_point'] - 0.5 if row['outcomes_name'] == 'Under' else (row['outcomes_point'] + 0.5 if row['outcomes_name'] == 'Over' else row['outcomes_point']), axis=1)


#######################################################################

#Calculate averages
for stat_to_pull in stats_to_pull:
    last_10_stats[stat_to_pull+'_avg'] = calculate_avg(last_10_stats,stat_to_pull,'count')

#Calculate Standard deviation
for stat_to_pull in stats_to_pull:
    last_10_stats[stat_to_pull+'_std'] = calculate_std(last_10_stats,stat_to_pull+'_deviation','count')

#Merge Prop and Stats
merge = pd.merge(prop_odds, last_10_stats, how='left', left_on='outcomes_description', right_on='First Last Name')

#Add opposing team and Defensive Ratings
merge['opposing team'] = merge.apply(lambda row: row['away_team'] if row['team'] == row['home_team'] else row['home_team'], axis=1)

merge.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\test.csv', header=True, index=False)

defensive_rating = pd.merge(defensive_rating, team_name_fix, how='left', left_on='team name', right_on='team name')
merge = pd.merge(merge, defensive_rating, how='left', left_on='opposing team', right_on='name fix')


#Add Outcome Last 10 Game Average - adjusted for specific stat
merge['Outcome Last 30 Avg'] = merge.apply(lambda row: row['points_avg'] if row['bookmakers.markets.key'] == 'player_points' 
                                 else (row['assists_avg'] if row['bookmakers.markets.key'] == 'player_assists' 
                                       else (row['totReb_avg'] if row['bookmakers.markets.key'] == 'player_rebounds' 
                                             else (row['tpm_avg'] if row['bookmakers.markets.key'] == 'player_threes'
                                                    else (row['Points_Rebounds_Assist_avg'] if row['bookmakers.markets.key'] == 'player_points_rebounds_assists'
                                                            else (row['Points_Rebounds_avg'] if row['bookmakers.markets.key'] == 'player_points_rebounds'
                                                                  else (row['Points_Assist_avg'] if row['bookmakers.markets.key'] == 'player_points_assists'
                                                                        else (row['Rebounds_Assist_avg'] if row['bookmakers.markets.key'] == 'player_rebounds_assists'
                                                                              else np.nan))))))), axis=1)

#Add Outcome of Last 30 day Standard Deviation - adjusted for specific stat
merge['Outcome Last 30 STD'] = merge.apply(lambda row: row['points_std'] if row['bookmakers.markets.key'] == 'player_points' 
                                 else (row['assists_std'] if row['bookmakers.markets.key'] == 'player_assists' 
                                       else (row['totReb_std'] if row['bookmakers.markets.key'] == 'player_rebounds' 
                                             else (row['tpm_std'] if row['bookmakers.markets.key'] == 'player_threes'
                                                    else (row['Points_Rebounds_Assist_std'] if row['bookmakers.markets.key'] == 'player_points_rebounds_assists'
                                                            else (row['Points_Rebounds_std'] if row['bookmakers.markets.key'] == 'player_points_rebounds'
                                                                  else (row['Points_Assist_std'] if row['bookmakers.markets.key'] == 'player_points_assists'
                                                                        else (row['Rebounds_Assist_std'] if row['bookmakers.markets.key'] == 'player_rebounds_assists'
                                                                              else np.nan))))))), axis=1)

#Add outcome of defensive ratins - adjusted for specific stat
merge['Defensive Rating Adjustment'] = merge.apply(lambda row: row['points_eff'] if row['bookmakers.markets.key'] == 'player_points' 
                                 else (row['assists_eff'] if row['bookmakers.markets.key'] == 'player_assists' 
                                       else (row['totReb_eff'] if row['bookmakers.markets.key'] == 'player_rebounds' 
                                             else (row['tpm_eff'] if row['bookmakers.markets.key'] == 'player_threes'
                                                    else (row['Points_Rebounds_Assist_eff'] if row['bookmakers.markets.key'] == 'player_points_rebounds_assists'
                                                            else (row['Points_Rebounds_eff'] if row['bookmakers.markets.key'] == 'player_points_rebounds'
                                                                  else (row['Points_Assist_eff'] if row['bookmakers.markets.key'] == 'player_points_assists'
                                                                        else (row['Rebounds_Assist_eff'] if row['bookmakers.markets.key'] == 'player_rebounds_assists'
                                                                              else np.nan))))))), axis=1)


#######################################################################
#CALCULATIONS
                                                                        
#Adjusting Last 30 for Defensive Rating
merge['Outcome Last 30 Avg Adjusted'] = merge['Outcome Last 30 Avg'] * merge['Defensive Rating Adjustment']

#Normalizing data on Variance to calculate percentage hit rate and EV
points_merge = process_data(merge,'Outcome Last 30 Avg','Outcome Last 30 Avg Adjusted')

#Filtering for specific bookmakers
points_merge = points_merge[points_merge['bookmakers.title'].isin(bookmaker_filter)]
columns_to_keep = [col for col in columns_to_keep if col in points_merge.columns]
points_merge = points_merge[columns_to_keep]

#######################################################################
#Outputs
points_merge['Date'] = today_date_str

#Historical output just for reference
points_merge.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\outputs\EV_Output_'+today_date_str+'.csv', header=True, index=False)

#Main Output
points_merge.to_csv(r'C:\Users\Brian\Main Folder\EV Bets\output_today\EV_Output.csv', header=True, index=False)
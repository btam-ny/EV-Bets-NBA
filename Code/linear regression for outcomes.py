import pandas as pd
import glob
import os
from sklearn.linear_model import LinearRegression
import datetime
from datetime import datetime

#####################################################################
#Loading in Files

current_directory = os.getcwd()
today_date = datetime.today().date()
today_date_str = today_date.strftime('%Y-%m-%d')

#Stats data
directory = glob.glob(os.path.join(current_directory,'data', 'stats_full_data', '*.csv'))
dfs = [pd.read_csv(file_path) for file_path in directory]
df = pd.concat(dfs, ignore_index=True)

#Lookups
file_path_defensive_rating = os.path.join(current_directory, 'data', 'team_defense_data', 'team_data_defense_last10.csv')
defensive_rating = pd.read_csv(file_path_defensive_rating)

file_path_prop_current = os.path.join(current_directory, 'data', 'prop_data', 'data_points_'+ today_date_str +'.csv')
prop_current = pd.read_csv(file_path_prop_current)

file_path_name_fix = os.path.join(current_directory, 'lookups', 'name_fix.csv')
name_fix = pd.read_csv(file_path_name_fix)

file_path_team_name_fix = os.path.join(current_directory, 'lookups', 'team_name_fix.csv')
team_name_fix = pd.read_csv(file_path_team_name_fix)

#####################################################################
#Team Name Fixes and Cleaning
# Create a mapping from 'team name' to 'team name odds'
team_name_mapping = team_name_fix.set_index('team name')['team name odds'].to_dict()

# Replace 'team name' in defensive_ratings
defensive_rating['team name'] = defensive_rating['team name'].map(team_name_mapping).fillna(defensive_rating['team name'])

df['Opposing Team'] = df.apply(lambda row: row['away_team'] if row['team'] == row['home_team'] else row['home_team'], axis=1)
df = df[['First Last Name', 'team', 'points', 'assists','totReb','tpm','Opposing Team']]

#Create new Columns for additional stats
df['Points_Rebounds_Assist'] = df['points'] + df['totReb'] + df['assists']
df['Points_Rebounds'] = df['points'] + df['totReb']
df['Points_Assist'] = df['points']+ df['assists']
df['Rebounds_Assist'] = df['totReb'] + df['assists']

#unpivot the data
df_melted = df.melt(id_vars=['First Last Name', 'team','Opposing Team'], value_vars=['points', 'assists','totReb','tpm','Points_Rebounds_Assist','Points_Rebounds','Points_Assist','Rebounds_Assist'], var_name='Statistic', value_name='Value')

def_melt = defensive_rating.melt(id_vars=['team name'], value_vars=['points_eff','assists_eff','tpm_eff','totReb_eff','Points_Rebounds_Assist_eff','Points_Rebounds_eff','Points_Assist_eff','Rebounds_Assist_eff'], var_name='Statistic', value_name='Defensive Rating')

def_melt['Statistic'] = def_melt['Statistic'].str.replace('_eff', '')

#####################################################################
#Merging Historical stats with defensive ratings
merged_df = df_melted.merge(def_melt, how='left', left_on=['Opposing Team', 'Statistic'], right_on=['team name', 'Statistic'])
merged_df = merged_df.drop('team name', axis=1)

# Create a mapping from 'team name' to 'team name odds'
name_fix_mapping = name_fix.set_index('Original Name')['Fixed Name'].to_dict()

# Replace 'team name' in defensive_ratings
prop_current['outcomes_description'] = prop_current['outcomes_description'].map(name_fix_mapping).fillna(prop_current['outcomes_description'])

#####################################################################
#Get Current Data and Data Cleaning

prop_current = prop_current[['outcomes_description','home_team','away_team']]
prop_current = prop_current.drop_duplicates()

df_team = merged_df[['First Last Name', 'team']]
df_team = df_team.drop_duplicates()

#Get opposing team for prop data
prop_current_team = prop_current.merge(df_team, how='left', left_on=['outcomes_description'], right_on=['First Last Name'])
prop_current_team['Opposing Team'] = prop_current_team.apply(lambda row: row['away_team'] if row['team'] == row['home_team'] else row['home_team'], axis=1)

#Clean prop data
prop_current_team = prop_current_team[['First Last Name','Opposing Team']]
prop_current_team = prop_current_team.rename(columns={'Opposing Team': 'Today Opposing Team'})

#Team name fix again
team_name_mapping_2 = team_name_fix.set_index('name fix')['team name odds'].to_dict()
prop_current_team['Today Opposing Team'] = prop_current_team['Today Opposing Team'].map(team_name_mapping_2).fillna(prop_current_team['Today Opposing Team'])


merged_df = merged_df.merge(prop_current_team, how='inner', left_on=['First Last Name'], right_on=['First Last Name'])


def_melt_today = def_melt.rename(columns={'Defensive Rating': 'Today Defensive Rating'})
merged_df = merged_df.merge(def_melt_today, how='left', left_on=['Today Opposing Team', 'Statistic'], right_on=['team name', 'Statistic'])

#####################################################################
#Linear Regression

filtered_df = merged_df[merged_df['Value'] != 0]


filtered_df_dedup = filtered_df[['First Last Name','Statistic','Today Defensive Rating']]
filtered_df_dedup = filtered_df_dedup.drop_duplicates()
filtered_df_dedup = filtered_df_dedup.rename(columns={'Today Defensive Rating': 'Defensive Rating'})
filtered_df_dedup.head()

# Get unique combinations of 'First Last Name' and 'Statistic'
combinations = filtered_df_dedup[['First Last Name', 'Statistic']].drop_duplicates().values

# Initialize a list to store predictions
predictions = []

# Loop over each combination
for first_last_name, statistic in combinations:
    # Filter the DataFrame for the current combination
    subset = filtered_df[(filtered_df['First Last Name'] == first_last_name) & (filtered_df['Statistic'] == statistic)]
    
    # Check if there are enough data points to fit the model
    if subset.shape[0] >= 2:
        # Define the features and target
        x = subset[['Defensive Rating']]
        y = subset['Value']
        
        # Fit the model
        reg = LinearRegression()
        reg.fit(x, y)
        
        # Get the 'Defensive Rating' from 'filtered_df_dedup' for the prediction
        x_new = filtered_df_dedup[(filtered_df_dedup['First Last Name'] == first_last_name) & (filtered_df_dedup['Statistic'] == statistic)][['Defensive Rating']]
        
        # Make predictions
        subset_predictions = reg.predict(x_new)
        
        # Store predictions in the list
        for prediction in subset_predictions:
            predictions.append([first_last_name, statistic, prediction])

# Convert the list to a DataFrame
predictions_df = pd.DataFrame(predictions, columns=['First Last Name', 'Statistic', 'Prediction'])

replace_dict = {
    'points': 'player_points',
    'assists': 'player_assist',
    'totReb': 'player_rebounds',
    'tpm': 'player_threes',
    'Points_Rebounds_Assist': 'player_points_rebounds_assists',
    'Points_Rebounds': 'player_points_rebounds',
    'Points_Assist': 'player_points_assists',
    'Rebounds_Assist': 'player_rebounds_assists'
}

predictions_df['Statistic'] = predictions_df['Statistic'].replace(replace_dict)

filename_predictions_df = 'predictions_df.csv'
full_path_predictions_df = os.path.join(current_directory, 'data','linear regression predictions', filename_predictions_df)
predictions_df.to_csv(full_path_predictions_df, header=True)
print('Linear Regression Complete')



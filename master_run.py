import subprocess
import os


current_directory = os.getcwd()

odds_pull = os.path.join(current_directory, 'Code', 'odds_nba.py')
stats_pull = os.path.join(current_directory, 'Code', 'stats_nba.py')
team_stats_pull = os.path.join(current_directory, 'Code', 'stats_nba_teams.py')
linear_regression = os.path.join(current_directory, 'Code', 'linear_regression_for_outcomes.py')
output = os.path.join(current_directory, 'Code', 'output_nba.py')

# Run the scripts
subprocess.run(['python', odds_pull])
subprocess.run(['python', stats_pull])
subprocess.run(['python', team_stats_pull])
subprocess.run(['python', linear_regression])
subprocess.run(['python', output])
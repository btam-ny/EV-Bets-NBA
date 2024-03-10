import subprocess
import os


current_directory = os.getcwd()

odds_pull = os.path.join(current_directory, 'Code', 'odds_nba.py')
stats_pull = os.path.join(current_directory, 'Code', 'stats_nba.py')
team_stats_pull = os.path.join(current_directory, 'Code', 'stats_nba_teams.py')
output = os.path.join(current_directory, 'Code', 'output_nba.py')

#odds_pull = "C:\\Users\\Brian\\Main Folder\\EV Bets\\Code\\odds_nba.py"
#stats_pull = "C:\\Users\\Brian\\Main Folder\\EV Bets\\Code\\stats_nba.py"
#team_stats_pull = "C:\\Users\\Brian\\Main Folder\\EV Bets\\Code\\stats_nba_teams.py"
#output = "C:\\Users\\Brian\\Main Folder\\EV Bets\\Code\\output_nba.py"

# Run the scripts
subprocess.run(['python', odds_pull])
subprocess.run(['python', stats_pull])
subprocess.run(['python', team_stats_pull])
subprocess.run(['python', output])
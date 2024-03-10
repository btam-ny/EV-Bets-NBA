NBA Prop Odds Expected Value
- Pulls in prop odds from bookmakers, and last 10 day stats to calculate if a current prop is positive or negative EV (expected value)


- Code
    - odds_nba: Pulls in prop odds for the current day
    - stats_nba: Pulls in stats from players from the previous day and appends historical data
    - stats_nba_teams: Pulls in team stats from previous day and appends historical data
    - output_nba: Does the calculations and outputs files that can be fed into PowerBI
  
- Stat Adjustments
  - Defense player stats are adjusted based on the amount of stats (points/reb/assists/threes/etc..) the team is allowing over the last 10 games
    - IE. Jalen Brunson is averaging 30 points over the last 10 games. He is playing the Timberwolves who allow 95% points compared to league average. His expected points are adjusted to 28.5 (.95 *30)
  - Adjusted player stats are fed into a normal distribution based on the player variance per game. % Chance of hitting a players prop line is calculated and then compared to what the actual % the bookmakers calculated
 
- Data Modeling and Data Visualization done in Power BI
  - Player Profile: Shows last 10 game stats of players playing today
    - Toggles for Points/Assists/Rebounds/Threes/etc..
    - Shows Over/Under, and hit rate over last 10 games
    - Calculates expected outcome (based on defense)
    - Shows the expected value for the over/under as well as variance in stats
  - Best Plays: Shows positive Expected Value and low variance plays
    - Filter by stats, bookmaker and team
    - Shows Expected value by Over/Under and all prop stats
  - Hit Rate with Matchup
    - Shows plays by hit rate over the last 10 games
    - Shows Expected Value and Defensive ratings to make better decisions
  - Yesterdays Results
    - Shows the lines from yesterday and if a player hit the over or under
    - Included a dashboard for individual players

  - Upcoming Features
    - Incorporating injuries and specific lineups teams play for adjusting player stats
  

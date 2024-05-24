NBA Prop Odds Expected Value

Pulls in prop odds from bookmakers and historical stats to calculate if a current prop has positive or negative EV (expected value)
Uses linear regression to predict the outcome of a players stats based on opposing teams defensive efficiency. Uses this predicted stat outcome to determine if a bookmakers lines have a positive or negative EV.

- Tools
    - Python: Used to pull data from APIs, cleaning, calculations and organizing dataframes
    - PowerBI: Used for data modeling and visualization
 
- APIs used
    - Rapid API-NBA: For Stats
        - https://rapidapi.com/api-sports/api/api-nba
    - The Odds API: For Prop Odds
        - https://the-odds-api.com
    - Environmental Variables needed to access. Place in Code folder
        - stats_api_key = "INSERT STATS API HERE"
        - odds_api_key = "INSERT ODDS API HERE"

- Code
    - odds_nba: Pulls in prop odds for the current day
    - stats_nba: Pulls in stats from players from the previous day and appends historical data
    - stats_nba_teams: Pulls in team stats from previous day and appends historical data
    - linear_regression_for_outcomes: Performs a linear regression analysis to predict player outcomes against defenses
    - output_nba: Does the calculations and outputs files that can be fed into PowerBI
  
- Features
  - Data is pulled in from 2 seperate APIs (odds and stats)
  - Prop Stats included
      - Points, Assists, Rebounds, Threes, Points + Rebounds + Assists, Points + Rebounds, Points + Assists, Rebounds + Assists
  - Uses linear regression to predict the outcome of the stats above
      - Model is trained on players previous outcomes vs. defensive efficiencies and predicted based on the team they are currently playing
      - This is specific to the stat type and based on 'Stat' per possession
        - IE. Assist allowed per possession is calculated per team, and compared to league average. This adjustment is fed into the model with players past performances against similarily rated defenses. An outcome is projected based on who the player is currently playing
  - Adjusted player stats from linear regression are fed into a normal distribution based on the player variance per game
      - % Chance of hitting a players prop line is calculated and then compared to what the actual % the bookmakers calculated (Expected Value)
  - Shows historical prop line for tracking changes in bookmaker odds
  - Shows multiple bookmakers odds for better decision making
  - Auto runs every morning using task scheduler and a batch file
 
- Data Modeling and Data Visualization done in Power BI
  - Player Profile: Shows last 10 game stats of players playing today
    - Toggles for Points/Assists/Rebounds/Threes/etc..
    - Togle Plyer up top
    - Shows Over/Under, and hit rate over last 10 games
    - Calculates expected outcome (based on predicted outcome of Linear  Regression vs. defenses)
    - Shows the expected value for the over/under as well as variance in stats
      - Expected value is: (Odds calculated by model of hiting) / (Odds from bookmaker: True Odds with Vig taken out)
  - Best Plays: Shows positive Expected Value and low variance plays
    - Filter by stats, bookmaker and team
    - Shows Expected value by Over/Under and all prop stats
  - Full Data Set
    - Most of the data available for sorting and filtering
  - Hit Rate with Matchup: Over/Under
    - Shows plays by hit rate over the last 10 games
    - Shows Expected Value and Defensive ratings to make better decisions
    - Seperated into Over and Under
  - Yesterdays Results
    - Shows the lines from yesterday and if a player hit the over or under
    - Included a dashboard for individual players

  - Upcoming Features
    - Incorporating injuries and specific lineups teams play for adjusting player stats
    - Adding in additional stats
    - Adding in information on alternate prop lines and what to adjust alternative prop lines to to maximize EV
    - Cleaning up data pull
    - Defense of team against specific positions
  

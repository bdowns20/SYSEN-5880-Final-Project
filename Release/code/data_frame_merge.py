#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import warnings

'''
Download the Kaggle data set:
https://www.kaggle.com/maxhorowitz/nflplaybyplay2009to2016?select=NFL+Play+by+Play+2009-2018+%28v5%29.csv
Rename NFL Play by Play 2009-2018 (v5).csv to nfl_play_by_play09-18.csv and place in the data directory
Let this run
'''

warnings.filterwarnings("ignore")

print('Loading in CSVs')
# Load the csv data
pbp = pd.read_csv("/Users/barrettdowns/NFL_draft/data/nfl_play_by_play09-18.csv", low_memory=False)
scores = pd.read_csv("/Users/barrettdowns/NFL_draft/data/spreadspoke_scores.csv", encoding='utf-8')
officials_data = pd.read_csv("/Users/barrettdowns/NFL_draft/data/officials.csv", encoding='utf=8')
games_data = pd.read_csv("/Users/barrettdowns/NFL_draft/data/games.csv", encoding='utf=8')
player_stats = pd.read_csv("/Users/barrettdowns/NFL_draft/data/nfl_player_stats.csv", encoding='utf-8')
teams = pd.read_csv("/Users/barrettdowns/NFL_draft/data/nfl_teams.csv", encoding='utf-8')
team_data = pd.read_csv("/Users/barrettdowns/NFL_draft/data/nfl_team_data.csv", encoding='utf=8')
idmap = pd.read_csv('/Users/barrettdowns/NFL_draft/data/game_id_map.csv')
weather = pd.read_csv("/Users/barrettdowns/NFL_draft/data/all_games_weather.csv", encoding='utf-8')

idmap = idmap.loc[idmap['type'] == 'reg']
idmap = idmap.drop(columns=['type','state_of_game','game_url','home_score','away_score'])

idmap['game_id'] = idmap.game_id.astype(str)
pbp['game_id'] = pbp.game_id.astype(str)

# fix the weather data
weather['schedule_date'] = pd.to_datetime(weather['date'])
weather = weather.drop(weather.columns[0], axis=1)
weather = weather.drop(columns=['stadium', 'score_away','score_home'])
weather.max_windgust.fillna(0, inplace=True)
weather.windchill.fillna(0, inplace=True)
weather.windchill_gust.fillna(0, inplace=True)
weather.avg_humidity.fillna(0, inplace=True)
weather.avg_dewpoint.fillna(0, inplace=True)
temp_bins = [-5,15,25,35,45,55,65,75,85,95,105]

weather['temp_range'] = pd.cut(weather.avg_temp, bins=temp_bins, duplicates='drop')
weather['wind_bins'] = pd.cut(weather.avg_wind, bins=[-0.1,10,15,20,41])

# Filter out all plays that aren't part of our target group
pbp = pbp[pbp['play_type'].isin(['pass', 'run', 'punt', 'field_goal'])]

# replace the target with ints
pbp.replace({ 'play_type': { 'pass': 0, 'run': 1, 'punt': 2, 'field_goal': 3 }}, inplace=True)

# Replace game_half string values with ints
pbp.replace({ 'game_half': { 'Half1': 1, 'Half2': 2, 'Overtime': 3 }}, inplace=True)

print('Filtering spreadspoke')
# Filter spreadspoke scores for only non-playoff season games 2004 through 2019
scores = scores.loc[(scores['schedule_season'] >= 2004) 
                    & (scores['schedule_season'] < 2019)
                    & (scores['schedule_playoff'] == False)]

# Reformat spreadspoke scores date column to match games date column format
scores['schedule_date'] = pd.to_datetime(scores['schedule_date'])
scores['schedule_week'] = scores.schedule_week.astype(int)

# Filter games data for only regular season games
reg_games = games_data[(games_data['seasonType'] == 'REG')]

scores = pd.merge(left=scores, left_on=['schedule_date','team_home','team_away'], right=weather, right_on=['schedule_date','home','away'])

# create a column if the game was indoors
scores.loc[(scores.weather_detail == 'DOME'), 'indoors'] = 1
scores.indoors.fillna(0, inplace=True)

# drop the columns 
scores = scores.drop(columns=['weather_temperature', 'weather_wind_mph', 'weather_humidity', 'weather_detail', 'date', 
'home', 'away', 'game_id'])

# great weather defined as wind under 5mph, temp bw 60-80, clear sky and no precipitation
scores.loc[(scores.indoors == 1) | (scores.avg_wind < 5) & (scores.avg_temp > 60) & (scores.avg_temp < 80) & (scores.precipitation=='None') & (scores.sky == 'clear'), 'great_conditions'] = 1
scores.great_conditions.fillna(0, inplace=True)

print('Filter player stats')
# Filter player_stats for 2002 and onward
player_stats['position'] = player_stats['position'].str.upper()
player_stats.drop_duplicates(subset=None, keep="first", inplace=True)
player_stats = player_stats.loc[player_stats['year'] >= 2002]

# Normalize seasonal team stats
scaler = StandardScaler()

# Exclude string and rating features from normalization
colsToNormalize = team_data[team_data.columns.difference(['schedule_season',
                                        'team_home', 
                                        'off_rate', 
                                        'def_rate', 
                                        'overall_rate', 
                                        'sched_strength'])].columns

for col in colsToNormalize:
    team_data[col] = scaler.fit_transform(team_data[col].values.reshape(-1, 1))

# Filter for only head referee
officials_data = officials_data.loc[officials_data['officialPosition'] == 'Referee']

# Combine games data with officials data
# this will help link to scores data since that doens't doesn't a correlating gameId
games_w_officials = pd.merge(left=reg_games, right=officials_data, how='left', left_on='gameId', right_on='gameId')

# Drop unnecessary columns
games_w_officials = games_w_officials[['gameId', 
                                       'gameDate', 
                                       'homeTeamFinalScore', 
                                       'visitingTeamFinalScore', 
                                       'officialId', 
                                       'officialName', 
                                       'officialPosition']]
games_w_officials['gameDate'] = pd.to_datetime(games_w_officials['gameDate'])

# ** NOTE: Games data starts at 2004, so we'll be missing two years of officials data if we start at 2002 **

print('Combining scores and officials')

# Combine scores data with combined games and officials data
scores = pd.merge(scores, games_w_officials, how='left', 
                left_on=['schedule_date', 'score_home', 'score_away'],
                right_on=['gameDate', 'homeTeamFinalScore', 'visitingTeamFinalScore'])

# Remove duplicated columns from officials game data
scores = scores.drop(columns=['gameDate', 'homeTeamFinalScore', 'visitingTeamFinalScore'])

print('Mapping names')
# Map team names to the correct/consistent team ids
scores['team_home'] = scores['team_home'].map(teams.set_index('team_name')['team_id'].to_dict())
scores['team_away'] = scores['team_away'].map(teams.set_index('team_name')['team_id'].to_dict())
team_data['team_home'] = team_data.team_home.map(teams.set_index('team_id_pfr')['team_id'].to_dict())

# add in the game id to match it with the play by play
scores = pd.merge(scores, idmap, how='inner', on=['schedule_season', 'schedule_week', 'team_home', 'team_away'])

player_stats['team'] = player_stats.team.map(teams.set_index('team_id_pfr')['team_id'].to_dict())

print('Mering scores and team ratings')
# Merge in home team season ratings
scores = scores.merge(team_data.add_suffix('_home'), how='left', 
                                        left_on=['schedule_season', 'team_home'],
                                        right_on=['schedule_season_home', 'team_home_home'])

# Merge in away season ratings
scores = scores.merge(team_data.add_suffix('_away'), how='left',
                                  left_on=['schedule_season', 'team_away'],
                                  right_on=['schedule_season_away', 'team_home_away'])
# init to 0 since the modifiers are all positive
# -1: no qb probowler on roster, 0: qb probowler on roster, didn't play, 1: qb probowler on roster, played
scores.insert(len(scores.columns), 'home_qb_modifier', 0.0)

# -1: no off probowlers on roster, 0 to 1: % of off probowlers on roster that played
scores.insert(len(scores.columns), 'home_off_modifier', 0.0)

# -1: no def probowlers on roster, 0 to 1: % of def probowlers on roster that played
scores.insert(len(scores.columns), 'home_def_modifier', 0.0)

# -1: no qb probowler on roster, 0: qb probowler on roster, didn't play, 1: qb probowler on roster, played
scores.insert(len(scores.columns), 'away_qb_modifier', 0.0)

# -1: no off probowlers on roster, 0 to 1: % of off probowlers on roster that played
scores.insert(len(scores.columns), 'away_off_modifier', 0.0)

# -1: no def probowlers on roster, 0 to 1: % of def probowlers on roster that played
scores.insert(len(scores.columns), 'away_def_modifier', 0.0)

# create list of offensive and defensive positions
offensive_pos = [
    'QB',
    'RB',
    'LT',
    'LG',
    'C',
    'RG',
    'RT',
    'TE',
    'WR',
    'FB',
    'C-TE',
    'PR-WR',
    'KR-CB',
    'G',
    'G-C-T',
    'G/RG',
    'K',
    'LS',
]

defensive_pos = [
    'FS',
    'SS',
    'RCB',
    'LCB',
    'RDE',
    'LILB',
    'LLB',
    'LDE',
    'MLB',
    'RLB',
    'ROLB',
    'LOLB',
    'OLB',
    'S'
    'RDT',
    'LB',
    'DT',
    'DE',
    'DB',
    'CB/RCB',
    'CB/LCB',
    'DE-C',
    'DE/RDE',
    'DT/LB',
    'DT/RDE',
    'DT/RDT',
    'EDGE',
    'DL',
    'IL/RILB',
    'LDT',
    'NT'
]

print('Adding in pro bowlers')
for year in range(2004, 2019):
    for team in scores['team_home'].unique():
        # get the special players for the team and season
        tdf = player_stats.loc[((player_stats['team'] == team) & (player_stats['year'] == year))]
        if len(tdf) != 0:
            # now split it to defense and offense
            offense = tdf.loc[(tdf['position'].isin(offensive_pos))]
            defense = tdf.loc[(tdf['position'].isin(defensive_pos))]
            qb_probowlers = tdf.loc[tdf['position'] == 'QB']

            for i in range(1, 18):
                home_game = scores.loc[(scores['schedule_season'] == year)
                                            & (scores['schedule_week'] == i)
                                            & (scores['team_home'] == team)]      
                away_game = scores.loc[(scores['schedule_season'] == year)
                                            & (scores['schedule_week'] == i)
                                            & (scores['team_away'] == team)]

                wk = 'w' + str(i)
                if len(offense) != 0:
                    # now we want a list of all offensive players who played during the week
                    count = len(offense.loc[(offense[wk] == 1)])
                    if not home_game.empty:
                        # fill in the home data
                        scores.loc[home_game.index, 'home_off_modifier'] = count / len(offense)
                    elif not away_game.empty:
                        # fill in the away data
                        scores.loc[away_game.index, 'away_off_modifier'] = count / len(offense)
                if len(defense) != 0:
                    # now we want a list of all defensive players who played during the week
                    count = len(defense.loc[(defense[wk] == 1)])
                    if not home_game.empty:
                        # fill in the home data
                        scores.loc[home_game.index, 'home_def_modifier'] = count / len(defense)
                    elif not away_game.empty:
                        # fill in the away data
                        scores.loc[away_game.index, 'away_def_modifier'] = count / len(defense)
                if not qb_probowlers.empty:
                    if not home_game.empty:
                        scores.loc[home_game.index, 'home_qb_modifier'] = qb_probowlers.iloc[0][wk]
                    elif not away_game.empty:
                        scores.loc[away_game.index, 'away_qb_modifier'] = qb_probowlers.iloc[0][wk]

# merge in the play by play
print('Merging in the play by play data...be patient')
scores = pd.merge(scores, pbp, how='inner', on=['game_id'])

# fill in the blanks with zeroes
scores.air_epa.fillna(0, inplace=True)
scores.yac_epa.fillna(0, inplace=True)
scores.comp_air_epa.fillna(0, inplace=True)
scores.comp_yac_epa.fillna(0, inplace=True)
scores.air_wpa.fillna(0, inplace=True)
scores.yac_wpa.fillna(0, inplace=True)
scores.comp_air_wpa.fillna(0, inplace=True)
scores.comp_yac_wpa.fillna(0, inplace=True)
scores.epa.fillna(0, inplace=True)
scores.wpa.fillna(0, inplace=True)
scores.home_wp_post.fillna(0, inplace=True)
scores.away_wp_post.fillna(0, inplace=True)
scores.gameId.fillna(0, inplace=True)
scores.officialId.fillna(0, inplace=True)
scores.ep.fillna(0, inplace=True)
scores.wp.fillna(0, inplace=True)
scores.def_wp.fillna(0, inplace=True)
scores.home_wp.fillna(0, inplace=True)
scores.away_wp.fillna(0, inplace=True)
scores.return_yards.fillna(0, inplace=True)

print('Saving data frame to CSV...please wait')
#save to disk
scores.to_csv("/Users/barrettdowns/NFL_draft/data/nfl_dataset_merged.csv", index=False)

scores.info()

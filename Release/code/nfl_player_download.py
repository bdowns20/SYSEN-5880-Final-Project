#!/usr/bin/env python3

from bs4 import BeautifulSoup
import time
from timeit import default_timer as timer
import pandas as pd
import numpy as np
import re
import requests
from sportsreference.nfl.teams import Teams
from sportsreference.nfl.roster import Player
from sportsreference.nfl.roster import Roster
import os

'''
Script downloads all player stats for Pro Bowl and All Pro players

This script will take a while to run, please be patient
'''

# pro bowl url
pro_bowl_url = 'https://www.pro-football-reference.com/years/{}/probowl.htm'
# all pro url
all_pro_url = 'https://www.pro-football-reference.com/years/{}/allpro.htm'
# game log url
game_log_url = 'https://www.pro-football-reference.com/players/{}/{}/gamelog/{}/'

teams = pd.read_csv("../data/nfl_teams.csv", encoding='utf-8')
teams = teams[['team_id', 'team_id_pfr']]
teams.drop_duplicates(subset=None, keep="first", inplace=True)

# mapping team ids to the correct teams
team_map = teams.set_index('team_id')['team_id_pfr'].to_dict();
team_map.update(teams.set_index('team_id_pfr')['team_id'].to_dict())

# create the data frame that will store all the player details
column_names = [
    'year',
    'team',
    'player_id',
    'player_name',
    'position',
    'total_games_played',
    'w1',
    'w2',
    'w3',
    'w4',
    'w5',
    'w6',
    'w7',
    'w8',
    'w9',
    'w10',
    'w11',
    'w12',
    'w13',
    'w14',
    'w15',
    'w16',
    'w17',
    'approximate_value',
    'adjusted_net_yards_per_attempt_index',
    'adjusted_yards_per_attempt',
    'adjusted_yards_per_attempt_index',
    'all_purpose_yards',
    'attempted_passes',
    'completed_passes',
    'completion_percentage_index',
    'field_goals_attempted',
    'field_goals_made',
    'fumbles',
    'interceptions_thrown',
    'interceptions',
    'interception_percentage_index',
    'longest_pass',
    'longest_reception',
    'longest_rush',
    'passing_yards',
    'quarterback_rating',
    'receiving_touchdowns',
    'receiving_yards',
    'receptions',
    'rush_attempts',
    'rush_touchdowns',
    'rush_yards',
    'yards_recovered_from_fumble',
    'yards_returned_from_interception'
]
startTime = timer()
player_file = '../data/nfl_player_stats.csv'
if os.path.exists(player_file):
    os.remove(player_file)

file = open(player_file, 'a')

for year in range(2002, 2020):
    df = None
    print('Getting award roster data for ' + str(year) + ' season')
    print('Pro Bowl')
    url = pro_bowl_url.format(year)
    df = pd.read_html(url)[0]
    df = df[['Player', 'Tm']]
    df.insert(0, 'Year', year)
    df['team_pfd'] = df.Tm.map(team_map)
    
    # now get the all pro
    print('All Pro')
    url = all_pro_url.format(year)
    ap = pd.read_html(url)[0]
    ap = df[['Player', 'Tm']]
    ap.insert(0, 'Year', year)
    ap['team_pfd'] = ap.Tm.map(team_map)
    df = df.append(ap)

    df.drop_duplicates(subset=None, keep="first", inplace=True)

    teams = Teams(year)
    for team in teams:
        print('TEAM: '+ team.abbreviation)
        # due to the team abbreviations...search both markings and the year
        tdf = df.loc[(((df['Tm'] == team.abbreviation) | (df['team_pfd'] == team.abbreviation)) & (df['Year'] == year))]

        # get just the list of player names and their id
        roster = Roster(team.abbreviation, year, True)

        # need to get the player id so we can get their stats
        player_names = tdf.Player.tolist()
        for name in player_names:
            name = re.sub(r'\s*(\%|\+)', '', name)
            print('Player: ' + name)
            pid = list(roster.players.keys())[list(roster.players.values()).index(name)]

            # game log data is not included in the api, so we need to look at the player's individual page for the particaular year
            url = game_log_url.format(pid[0], pid, year)
            gl = pd.read_html(url)[0]
            weeks_played = gl.iloc[:, 3].tolist()
            map(int, weeks_played)

            # create a map of all games, 1 = played, 0 = did not play
            # also, kickers don't have a total number of games played
            weeks = {}
            total_games = 0;
            for i in range(1,18):
                weeks[i] = 0
                if i in weeks_played:
                    total_games = total_games + 1
                    weeks[i] = 1

            # get the player object based on the player id
            player = Player(pid)

            # if a player is a kicker, they don't have a position...dropping all kickers, not worth it
            # should probably also drop others that won't have data like offensive linesmen...something to think about
            position = ''
            try:
                position = player(str(year)).position
                if not position:
                    html_text = requests.get(url).text
                    soup = BeautifulSoup(html_text, 'html.parser')
                    for p in soup.find_all('p'):
                        if 'Position'in p.text:
                            position = p.text.replace('Position: ','')
                            position = re.sub(r'\s+', '', position)
                            break
            except:
                print('Skipping: ' + name)
                continue
            
            # now we have a list of games this person actually played in we can fill out the dataframe
            player_stats = [[
                year,
                team.abbreviation,
                pid,
                name,
                position,
                total_games,
                weeks[1],
                weeks[2],
                weeks[3],
                weeks[4],
                weeks[5],
                weeks[6],
                weeks[7],
                weeks[8],
                weeks[9],
                weeks[10],
                weeks[11],
                weeks[12],
                weeks[13],
                weeks[14],
                weeks[15],
                weeks[16],
                weeks[17],
                player(str(year)).approximate_value,
                player(str(year)).adjusted_net_yards_per_attempt_index,
                player(str(year)).adjusted_yards_per_attempt,
                player(str(year)).adjusted_yards_per_attempt_index,
                player(str(year)).all_purpose_yards,
                player(str(year)).attempted_passes,
                player(str(year)).completed_passes,
                player(str(year)).completion_percentage_index,
                player(str(year)).field_goals_attempted,
                player(str(year)).field_goals_made,
                player(str(year)).fumbles,
                player(str(year)).interceptions_thrown,
                player(str(year)).interceptions,
                player(str(year)).interception_percentage_index,
                player(str(year)).longest_pass,
                player(str(year)).longest_reception,
                player(str(year)).longest_rush,
                player(str(year)).passing_yards,
                player(str(year)).quarterback_rating,
                player(str(year)).receiving_touchdowns,
                player(str(year)).receiving_yards,
                player(str(year)).receptions,
                player(str(year)).rush_attempts,
                player(str(year)).rush_touchdowns,
                player(str(year)).rush_yards,
                player(str(year)).yards_recovered_from_fumble,
                player(str(year)).yards_returned_from_interception
            ]]

            # create the dataframe
            player_details = pd.DataFrame(player_stats, columns=column_names)

            # write it to disk after each player since there is so much data
            player_details.to_csv(file, mode='a', index=False, header=not file.tell())

endTime = timer()
print('It took ', (endTime - startTime) / 60, ' minutes to download the data.')

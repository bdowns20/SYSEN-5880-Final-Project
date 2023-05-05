#!/usr/bin/env python3

"""
nfl_team_download.py
This script utilizes the Sports Reference API to download the team data for the model

-----------------
--  CHANGE LOG --
-----------------
-Initial Commit
-Added in additional data columns for the team related information
"""

import argparse
from sportsreference.nfl.teams import Teams
from timeit import default_timer as timer
import csv

# API can be found here
# https://sportsreference.readthedocs.io/en/stable/nfl.html

# Create the parser
parser = argparse.ArgumentParser(description='NFL Team Data Download')

# Add the arguments
parser.add_argument('-d', '--data', metavar='data',
                       type=str, help='directory for saving data, default is data')

# Execute parse_args()
args = parser.parse_args()

dir = 'data'
if args.data:
    dir = args.data

startTime = timer()

# save the data to disk and reset the dictionaries
with open(dir+'/nfl_team_data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(
                ['schedule_season', 'team_home', 'off_rate', 'def_rate', 'overall_rate', 'sched_strength',
                'first_downs', 'first_downs_from_penalties', 'fumbles', 'interceptions', 'margin_of_victory',
                'pass_attempts', 'pass_completions', 'pass_first_downs', 'pass_touchdowns','pass_yards',
                'penalties', 'plays', 'points_against', 'points_contributed_by_offense', 'points_difference',
                'points_for', 'rank', 'rush_attempts', 'rush_first_downs', 'rush_touchdowns', 'rush_yards',
                'turnovers', 'yards', 'yards_from_penalties','yards_per_play'])

    # get all the data for each of the years
    for year in range(2002, 2020):
        print("Year: " + str(year))
        teams = Teams(year)

        for team in teams:
            print(team.name)

            csv_writer.writerow([year, team.abbreviation, team.offensive_simple_rating_system,
                                 team.defensive_simple_rating_system, team.simple_rating_system,
                                 team.strength_of_schedule, team.first_downs,team.first_downs_from_penalties, 
                                 team.fumbles, team.interceptions, team.margin_of_victory, team.pass_attempts, 
                                 team.pass_completions, team.pass_first_downs, team.pass_touchdowns, team.pass_yards,
                                 team.penalties, team.plays, team.points_against, team.points_contributed_by_offense,
                                 team.points_difference, team.points_for, team.rank, team.rush_attempts, 
                                 team.rush_first_downs, team.rush_touchdowns, team.rush_yards, team.turnovers, 
                                 team.yards, team.yards_from_penalties, team.yards_per_play])


endTime = timer()
print('It took ', (endTime - startTime) / 60, ' minutes to download the data.')

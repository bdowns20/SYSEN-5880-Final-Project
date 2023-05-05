#!/usr/bin/env python3

# This was taken from Reddit:
# - https://www.reddit.com/r/learnpython/comments/65rcn1/python_help_scraping_off_a_website_soupfindall/
# Provided by user Vaphell on April 16, 2017
#
# Changes:
# - added in ability to get weekly details for years 2009 - 2018 (only data available)
# - removed queries for all games that are not regular season
# - changed to the format to save  as a csv instead of printing to screen
# - changed the team names to match the abbreviations from the sports reference api

import time
from bs4 import BeautifulSoup
from timeit import default_timer as timer
import requests
import csv

# website for scraping the weather data
season_url = 'http://nflweather.com/en/week/{}/week-{}/'

# mappings for this website to the sports reference api
team_name = {'49ers': 'SFO', 'Bears': 'CHI', 'Bengals': 'CIN', 'Bills': 'BUF', 'Broncos': 'DEN', 'Browns': 'CLE',
             'Buccaneers': 'TAM', 'Cardinals': 'CRD', 'Chargers': 'SDG', 'Chiefs': 'KAN', 'Colts': 'CLT',
             'Cowboys': 'DAL', 'Dolphins': 'MIA', 'Eagles': 'PHI', 'Falcons': 'ATL', 'Giants': 'NYG',
             'Jaguars': 'JAX', 'Jets': 'NYJ', 'Lions': 'DET', 'Packers': 'GNB', 'Panthers': 'CAR', 'Patriots': 'NWE',
             'Raiders': 'RAI', 'Rams': 'RAM', 'Ravens': 'RAV', 'Redskins': 'WAS', 'Saints': 'NOR', 'Seahawks': 'SEA',
             'Steelers': 'PIT', 'Texans': 'HTX', 'Titans': 'OTI', 'Vikings': 'MIN'}


def game_data(date_str, game):
    teams = game.select('td.team-name a')
    guest, host = [team.text for team in teams]

    weather_short = game.select('td:nth-of-type(10)')[0].text.strip().replace(',', '')

    # if in a dome, then inside is set to 1
    inside = 0
    if weather_short == 'DOME':
        inside = 1

    return date_str + team_name[host] + ';' + str(inside) + ';' + weather_short


def games(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")
    return soup.select('table.table tbody tr')


def urls(year):
    for week in range(1, 18):
        url = season_url.format(year, week)
        yield url, week


if __name__ == '__main__':

    startTime = timer()

    with open('../data/nfl_game_weather_data.csv', 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['year', 'week', 'home', 'inside', 'weather_short'])
        for year in range(2009, 2019):
            print('Getting weather data for ' + str(year) + ' season')
            for url, week in urls(year):
                date_str = str(year) + ';' + str(week) + ';'
                for game in games(url):
                    row = game_data(date_str, game)
                    csv_writer.writerow(row.split(';'))
        time.sleep(1)

endTime = timer()
print('It took ', (endTime - startTime) / 60, ' minutes to download the data.')

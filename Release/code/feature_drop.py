#!/usr/bin/env python3

import argparse
import pandas as pd

# Create the parser
parser = argparse.ArgumentParser(description='Feature Dropper')

# Add the arguments
parser.add_argument('-f', '--file', metavar='data', required=True,
                       type=str, help='Full path to CSV to drop features from')
parser.add_argument('-s', '--save', metavar='data', required=False,
                       type=str, help='Full path and file name to save the data to')

# Execute parse_args()
args = parser.parse_args()

output = '/Users/barrettdowns/NFL_draft/data/dataset_complete.csv'
if args.save:
    output = args.save


########################################
#    'play_type', # THIS IS OUR TARGET
#########################################

# list the feature to drop
# include a comment about why if not obvious
drop = [
    'schedule_date',
    'schedule_season',
    'schedule_week',
    'timeout_team',
    'td_team',
    'penalty_team',
    'penalty_yards',
    'schedule_playoff', # regular, pre-season, or playoffs shouldn't matter
    'team_home', # team identifier
    'team_away', # team identifier
    'team_favorite_id', # team identifier
    'spread_favorite',
    'over_under_line',
    'stadium', # stadium name
    'stadium_neutral', # indicator if the stadium is on a neutral field
    'game_id', #not needed once the data frames are merged
    'officialName', # there is an official id
    'officialPosition', # they're all refs
    'schedule_season_home', # duplicate
    'team_home_home', # duplicate
    'schedule_season_away', # duplicate
    'team_home_away', #duplicate
    'play_id', # play index
    'home_team', # team identifier
    'away_team', # team identifier
    'game_date',
    'desc', # play description
    'yrdln', # the int equivalent column is 'yardline_100'
    'side_of_field', # an unnecessary string type column
    'penalty_type', # string describing the penalty
    # everything below here is play results (which we don't want for making predictions)
    'yards_gained',
    'qb_dropback',
    'qb_kneel',
    'qb_spike',
    'qb_scramble',
    'pass_length',
    'pass_location',
    'air_yards',
    'yards_after_catch',
    'run_location',
    'run_gap',
    'field_goal_result',
    'kick_distance',
    'extra_point_result',
    'two_point_conv_result',
    'punt_blocked',
    'first_down_rush',
    'first_down_pass',
    'first_down_penalty',
    'third_down_converted',
    'third_down_failed',
    'fourth_down_converted',
    'fourth_down_failed',
    'incomplete_pass',
    'interception',
    'punt_inside_twenty',
    'punt_in_endzone',
    'punt_out_of_bounds',
    'punt_downed',
    'punt_fair_catch',
    'kickoff_inside_twenty',
    'kickoff_in_endzone',
    'kickoff_out_of_bounds',
    'kickoff_downed',
    'kickoff_fair_catch',
    'fumble_forced',
    'fumble_not_forced',
    'fumble_out_of_bounds',
    'solo_tackle',
    'safety',
    'penalty',
    'tackled_for_loss',
    'fumble_lost',
    'own_kickoff_recovery',
    'own_kickoff_recovery_td',
    'qb_hit',
    'rush_attempt',
    'pass_attempt',
    'sack',
    'touchdown',
    'pass_touchdown',
    'rush_touchdown',
    'return_touchdown',
    'extra_point_attempt',
    'two_point_attempt',
    'field_goal_attempt',
    'kickoff_attempt',
    'punt_attempt',
    'fumble',
    'complete_pass',
    'assist_tackle',
    'lateral_reception',
    'lateral_rush',
    'lateral_return',
    'lateral_recovery',
    # everything below is just a player identifier
    'passer_player_id', 
    'passer_player_name', 
    'receiver_player_id', 
    'receiver_player_name', 
    'rusher_player_id', 
    'rusher_player_name', 
    'lateral_receiver_player_id', 
    'lateral_receiver_player_name', 
    'lateral_rusher_player_id', 
    'lateral_rusher_player_name', 
    'lateral_sack_player_id', 
    'lateral_sack_player_name', 
    'interception_player_id', 
    'interception_player_name', 
    'lateral_interception_player_id', 
    'lateral_interception_player_name', 
    'punt_returner_player_id', 
    'punt_returner_player_name', 
    'lateral_punt_returner_player_id', 
    'lateral_punt_returner_player_name', 
    'kickoff_returner_player_name', 
    'kickoff_returner_player_id', 
    'lateral_kickoff_returner_player_id', 
    'lateral_kickoff_returner_player_name', 
    'punter_player_id', 
    'punter_player_name', 
    'kicker_player_name', 
    'kicker_player_id', 
    'own_kickoff_recovery_player_id', 
    'own_kickoff_recovery_player_name', 
    'blocked_player_id', 
    'blocked_player_name', 
    'tackle_for_loss_1_player_id', 
    'tackle_for_loss_1_player_name', 
    'tackle_for_loss_2_player_id', 
    'tackle_for_loss_2_player_name', 
    'qb_hit_1_player_id', 
    'qb_hit_1_player_name', 
    'qb_hit_2_player_id', 
    'qb_hit_2_player_name', 
    'forced_fumble_player_1_team', 
    'forced_fumble_player_1_player_id', 
    'forced_fumble_player_1_player_name', 
    'forced_fumble_player_2_team', 
    'forced_fumble_player_2_player_id', 
    'forced_fumble_player_2_player_name', 
    'solo_tackle_1_team', 
    'solo_tackle_2_team', 
    'solo_tackle_1_player_id', 
    'solo_tackle_2_player_id', 
    'solo_tackle_1_player_name', 
    'solo_tackle_2_player_name', 
    'assist_tackle_1_player_id', 
    'assist_tackle_1_player_name', 
    'assist_tackle_1_team', 
    'assist_tackle_2_player_id', 
    'assist_tackle_2_player_name', 
    'assist_tackle_2_team', 
    'assist_tackle_3_player_id', 
    'assist_tackle_3_player_name', 
    'assist_tackle_3_team', 
    'assist_tackle_4_player_id', 
    'assist_tackle_4_player_name', 
    'assist_tackle_4_team', 
    'pass_defense_1_player_id', 
    'pass_defense_1_player_name', 
    'pass_defense_2_player_id', 
    'pass_defense_2_player_name',
    'fumbled_1_team', 
    'fumbled_1_player_id', 
    'fumbled_1_player_name', 
    'fumbled_2_player_id', 
    'fumbled_2_player_name', 
    'fumbled_2_team', 
    'fumble_recovery_1_team', 
    'fumble_recovery_1_yards', 
    'fumble_recovery_1_player_id', 
    'fumble_recovery_1_player_name', 
    'fumble_recovery_2_team', 
    'fumble_recovery_2_yards', 
    'fumble_recovery_2_player_id', 
    'fumble_recovery_2_player_name',
    'penalty_player_id', 
    'penalty_player_name'
]

print('Reading in original CSV')
df = pd.read_csv(args.file, low_memory=False)

print('Dropping ' + str(len(drop)) + ' features')
df = df.drop(columns=drop)

print('Saving new CSV')
df.to_csv(output, index=False)


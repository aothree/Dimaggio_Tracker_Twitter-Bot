# #!usr/bin/env Python3

import tweepy
import pandas as pd
import numpy as np
import requests
import re
import statsapi
import datetime 
from datetime import date
from hit_streak_scraper import scrape_baseball_musings 
import config

# dictionary of team abbreviations, team mascots, and twitter emoji hashtags
team_dict = {
    108: ('LAA', 'Angels', '#GoHalos'),
    109: ('ARI', 'D-backs', '#Dbacks'),
    110: ('BAL', 'Orioles', '#Birdland'),
    111: ('BOS', 'Red Sox', '#DirtyWater'),
    112: ('CHC', 'Cubs', '#ItsDifferentHere'),
    113: ('CIN', 'Reds', '#ATOBTTR'),
    114: ('CLE', 'Guardians', '#ForTheLand'),
    115: ('COL', 'Rockies', '#Rockies'),
    116: ('DET', 'Tigers', '#DetroitRoots'),
    117: ('HOU', 'Astros', '#LevelUp'),
    118: ('KC', 'Royals', '#TogetherRoyal'),
    119: ('LAD', 'Dodgers', '#AlwaysLA'),
    120: ('WSH', 'Nationals', '#NATITUDE'),
    121: ('NYM', 'Mets', '#LGM'),
    133: ('OAK', 'Athletics', '#DrumTogether'),
    134: ('PIT', 'Pirates', '#LetsGoBucs'),
    135: ('SD', 'Padres', '#TimeToShine'),
    136: ('SEA', 'Mariners', '#SeaUsRise'),
    137: ('SF', 'Giants', '#SFGameUp'),
    138: ('STL', 'Cardinals', '#STLCards'),
    139: ('TB', 'Rays', '#RaysUp'),
    140: ('TEX', 'Rangers', '#StraightUpTX'),
    141: ('TOR', 'Blue Jays', '#NextLevel'),
    142: ('MIN', 'Twins', '#MNTwins'),
    143: ('PHI', 'Phillies', '#RingTheBell'),
    144: ('ATL', 'Braves', '#ForTheA'),
    145: ('CWS', 'White Sox', '#ChangeTheGame'),
    146: ('MIA', 'Marlins', '#MakeItMiami'),
    147: ('NYY', 'Yankees', '#RepBX'),
    158: ('MIL', 'Brewers', '#ThisIsMyCrew')
}

# Twitter authentification 
consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_token_secret = config.access_token_secret

# accessing Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# get today's game ids.  Index 0 will give you all ids, Index 1 will just return active game ids
today_schedule = statsapi.schedule()

df_streaks = scrape_baseball_musings()

def get_active_game_ids():
    all_game_ids = []
    active_game_ids = []
    for i in range(len(today_schedule)):
        if today_schedule[i]['status'] == 'In Progress':
            all_game_ids.append(today_schedule[i]['game_id'])
            active_game_ids.append(today_schedule[i]['game_id'])
        else: 
            all_game_ids.append(today_schedule[i]['game_id'])
    return all_game_ids, active_game_ids

# create list to prevent more than 1 tweet about the same player on a given day
todays_tweets = []

# current hour
current_hour = datetime.datetime.now().hour

# grab time of last game today and convert to "datetime" format
last_game_time = pd.to_datetime(today_schedule[-1]['game_datetime'])

# converting from UTC to local time (PST)
last_game_time_converted = last_game_time.tz_convert('US/Pacific')

# Add four hours to the start-hour of the last game of the day
last_hour_plus_4 = last_game_time_converted.hour + 4 

# Run below code until 4 hours after the last game starts
while current_hour <= last_hour_plus_4:
    # loop through active games
    game_ids = get_active_game_ids()[1] 
    for game in game_ids:
        url = f'https://statsapi.mlb.com/api/v1/game/{game}/playByPlay'
        res = requests.get(url)
        data = res.json()
        for i in range(len(data['allPlays'])-1):
            try: 
                event = data['allPlays'][i]['result']['event']
            except:
                continue
            
            # Continue only for hits
            if event == 'Single' or event == 'Double' or event == 'Triple' or event == 'Home Run':
                
                if event == 'Home Run':
                    event_emoji = '\U0001F4A3\U0001F680'
                elif event == 'Single':
                    event_emoji = '\U00000031\U000020E3'
                elif event == 'Double':
                    event_emoji = '\U0000270C'
                elif event == 'Triple':
                    event_emoji = '\U0001F3C3\U0001F3C3\U0001F3C3' 
                
                # save name and last_name.  Suffixes like "Jr" will need to be added going forward
                name = data["allPlays"][i]["matchup"]["batter"]["fullName"]

                if name not in todays_tweets:
                    if 'Jr' in name:
                        last_name = ' '.join(name.split()[-2:])
                    else:
                        last_name = name.split()[-1]
                    
                    # identify what team batter is on
                    player_team_id = statsapi.lookup_player(name)[0]['currentTeam']['id']

                    #check df_streaks to see if player has a hitting streak of 5 or more games
                    if name in df_streaks['Player'].value_counts():
                        hit_streak = int(df_streaks.loc[(df_streaks['Player']== name)]['Games'].values[0]) + 1
                        print(name, hit_streak)
                    else:
                        continue

                    if hit_streak >= 5:
                        # save details from the hit to variables
                        pitcher_name = data['allPlays'][i]['matchup']['pitcher']['fullName']
                        pitch_type = data['allPlays'][0]['playEvents'][-1]['details']['type']['description']
                        pitch_speed = data['allPlays'][0]['playEvents'][-1]['pitchData']['startSpeed']
                        try:
                            exit_velo = data['allPlays'][i]['playEvents'][-1]['hitData']['launchSpeed']
                            # set emoji for exit velocity
                            if exit_velo > 110:
                                exit_velo_emoji = '\U0000203C'
                            elif exit_velo >= 100:
                                exit_velo_emoji = '\U000026A1'
                            elif exit_velo >= 90:
                                exit_velo_emoji = '\U0001F44F'
                            else:
                                exit_velo_emoji = ''
                        except:
                            exit_velo = 'Not Recorded'
                        
                        # set emoji for launch_angle
                        try: 
                            launch_angle = data['allPlays'][i]['playEvents'][-1]['hitData']['launchAngle']
                            if 25 <= launch_angle <= 35:
                                launch_angle_emoji = '\U0001F64C'
                            elif launch_angle < 10:
                                launch_angle_emoji = '\U0001F447'
                            else:
                                launch_angle_emoji = ''
                        except:
                            launch_angle_emoji = ''
                        
                        # set emoji for batting average 
                        batting_avg =  float(df_streaks.loc[(df_streaks['Player']== name)]['BA'].values[0])
                        
                        if .300 <= batting_avg < .400:
                            heat_check_emoji = '\U0001F440'
                        elif .400 <= batting_avg < .500:
                            heat_check_emoji = '\U0001F525'
                        elif batting_avg >= .500:
                            heat_check_emoji = '\U0001F60D'
                        else:
                            heat_check_emoji = ''
                        
                        # Fix batting average to be three significant digits                 
                        if len(str(batting_avg)) == 4:
                            avg_fixed = str(batting_avg) + '0'
                        elif len(str(batting_avg)) == 3:
                            avg_fixed = str(batting_avg) + '00'
                        else:
                            avg_fixed = batting_avg
                        avg_fixed = str(avg_fixed).lstrip('0')
                        
                        #Send Tweet
                        if event == 'Double':
                            upload_result = api.media_upload(r'utah_two.mp4')
                            text = f'{team_dict[player_team_id][-1]}\n\n{name} hit a {event.lower()}{event_emoji} off of an {pitch_speed} mph {pitch_type.lower()} from {pitcher_name}, and now has a {hit_streak} game hit streak.\n\nExit Velocity: {exit_velo} mph{exit_velo_emoji}\n\nLaunch Angle: {launch_angle} degrees{launch_angle_emoji}\n\n{last_name} is batting {avg_fixed} over this stretch.{heat_check_emoji}'
                            #print('tweet would be fired') # uncomment to debug, comment-out below tweet line
                            api.update_status(status = text, media_ids = [upload_result.media_id_string])
                            current_hour = datetime.datetime.now().hour 
                            current_time = datetime.datetime.now()
                            print(f'tweet fired for {name} at {current_time}')
                        else:
                            #print('tweet would be fired') #uncomment to debug, and comment below tweet line
                            api.update_status(f'{team_dict[player_team_id][-1]}\n\n{name} hit a {event.lower()}{event_emoji} off of an {pitch_speed} mph {pitch_type.lower()} from {pitcher_name}, and now has a {hit_streak} game hit streak.\n\nExit Velocity: {exit_velo} mph{exit_velo_emoji}\n\nLaunch Angle: {launch_angle} degrees{launch_angle_emoji}\n\n{last_name} is batting {avg_fixed} over this stretch.{heat_check_emoji}')
                            current_hour = datetime.datetime.now().hour
                            current_time = datetime.datetime.now()
                            print(f'tweet fired for {name} at {current_time}')                                                    
                        
                        todays_tweets.append(name)
                        break
                    else:
                        print(f"{name}'s hit streak is less than 5")
                        continue
                else:
                    print(f"{name} already tweeted about")
                    continue
            

                
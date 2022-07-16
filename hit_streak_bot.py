import tweepy
import pandas as pd
import numpy as np
import requests, bs4
import re, os
import matplotlib.pyplot as plt
import statsapi
from datetime import date
import credentials

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

todays_tweets = ['Austin Riley',
 'Gleyber Torres',
 'Teoscar Hernandez',
 'Amed Rosario',
 'Seth Brown',
 'Jose Abreu',
 'Jonathan India',
 'Charlie Blackmon',
 'Nelson Cruz',
 'Leody Taveras',
 'Brandon Drury',
 'Corey Seager',
 'Tyler Stephenson',
 "Ke'Bryan Hayes",
 'Trea Turner',
 'Andrew McCutchen',
 'Freddie Freeman']

consumer_key = credentials.API_key
consumer_secret_key = credentials.API_secret_key
access_token = credentials.access_token
access_token_secret = credentials.access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# get active game ids
def get_active_game_ids():
    today_schedule = statsapi.schedule()
    active_game_ids = []
    for i in range(len(today_schedule)):
        if today_schedule[i]['status'] == 'In Progress':
            active_game_ids.append(today_schedule[i]['game_id'])
    return active_game_ids

# get hit streak data, updated through yesterday's games
today = date.today()
today = str(today)[-2:]
today
url = f'https://www.baseballmusings.com/cgi-bin/CurStreak.py?EndDate=07%2F{today}%2F2022'
resp = requests.get(url)

with open('test_mlb_longesthitstreak', 'wb') as f:
    f.write(resp.content)

df_streaks = pd.read_html('test_mlb_longesthitstreak')
df_streaks = pd.DataFrame(df_streaks[1])

game_ids = get_active_game_ids()

# loop through active games
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
                event_emoji = '\U000026BE'
            elif event == 'Double':
                event_emoji = '\U0000270C'
            elif event == 'Triple':
                event_emoji = '\U0001F3C3\U0001F3C3, \U0001F3C3' 
            
            # save name and last_name.  Suffixes like "Jr" will need to be added going forward
            name = data["allPlays"][i]["matchup"]["batter"]["fullName"]
                      
            if name not in todays_tweets:
                if 'Jr' in name:
                    last_name = ' '.join(name.split()[-2:])
                else:
                    last_name = name.split()[-1]
                
                # identify what team batter is on
                player_team_id = statsapi.lookup_player(name)[0]['currentTeam']['id']

                #check to see if player has a hitting streak of 5 or more games
                if name in df_streaks['Player'].value_counts():
                    hit_streak = int(df_streaks.loc[(df_streaks['Player']== name)]['Games'].values[0]) + 1
                else:
                    continue
                
                if hit_streak >= 5:
                    print(name, hit_streak)
                    # save details from the hit to variables
                    pitcher_name = data['allPlays'][i]['matchup']['pitcher']['fullName']
                    pitch_type = data['allPlays'][0]['playEvents'][-1]['details']['type']['description']
                    pitch_speed = data['allPlays'][0]['playEvents'][-1]['pitchData']['startSpeed']
                    batting_avg =  float(df_streaks.loc[(df_streaks['Player']== name)]['BA'].values[0])
                    exit_velo = data['allPlays'][i]['playEvents'][-1]['hitData']['launchSpeed']
                    launch_angle = data['allPlays'][i]['playEvents'][-1]['hitData']['launchAngle']
                    
                    # set emoji for different batting average levels
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
                    
                    # Send Tweet
                    if event == 'Double':
                        upload_result = api.media_upload(r'C:\Users\aorfa\Downloads\Utah_Get_Me_Two.mp4')
                        text = f'{team_dict[player_team_id][-1]}\n\n{name} hit a {event.lower()}{event_emoji} off of a {pitch_speed} mph {pitch_type.lower()} from {pitcher_name}, and now has a {hit_streak} game hit streak.\n\nExit Velocity: {exit_velo} mph\n\nLaunch Angle: {launch_angle} degrees\n\n{last_name} is batting {avg_fixed} over this stretch.{heat_check_emoji}'
                        api.update_status(status = text, media_ids = [upload_result.media_id_string])
                        print(f'tweet fired for {name}')
                    else:
                        api.update_status(f'{team_dict[player_team_id][-1]}\n\n{name} hit a {event.lower()}{event_emoji} off of a {pitch_speed} mph {pitch_type.lower()} from {pitcher_name}, and now has a {hit_streak} game hit streak.\n\nExit Velocity: {exit_velo} mph\n\nLaunch Angle: {launch_angle} degrees\n\n{last_name} is batting {avg_fixed} over this stretch.{heat_check_emoji}')
                        print(f'tweet fired for {name}')                                                     
                    
                    # Add name to list so that another a hit from the player won't trigger a tweet.
                    todays_tweets.append(name)
                    break
                else:
                    print(f"{name}'s hit streak is less than 5")
                    continue
            else:
                print(f'{name} already tweeted about')
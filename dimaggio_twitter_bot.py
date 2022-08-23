# #!usr/bin/env Python3

import tweepy
import pandas as pd
import numpy as np
import requests
import re
import statsapi
import datetime
from datetime import datetime
from hit_streak_scraper import scrape_baseball_musings
import config
import pickle
import boto3

# reset tweets list every morning between 9-10am PST.  This erases all players names from the previous days tweets.

time = datetime.now()
if time.hour() == 9:
    bucket=config.bucket
    key=config.key
    s3 = boto3.resource('s3')
    previous_content = pickle.loads(s3.Bucket(bucket).Object(key).get(['Body'].read())
    yday_tweets = previous_content.split(',') 
    print(f'Yesterday's tweets: {yday_tweets}')
          
    # Empty pkl file.  New day, so no one has been tweeted about yet.  
    pickle_byte_obj = pickle.dumps('') 
    s3_resource.Object(bucket,key).put(Body=pickle_byte_obj)
    
    print(f'tweet list in s3 bucket cleared of players at: {time}')
    

# dictionary of team abbreviations, team mascots, and twitter emoji hashtags
team_dict = team_dict = {
    108: ("LAA", "Angels", "#GoHalos"),
    109: ("ARI", "D-backs", "#Dbacks"),
    110: ("BAL", "Orioles", "#Birdland"),
    111: ("BOS", "Red Sox", "#DirtyWater"),
    112: ("CHC", "Cubs", "#ItsDifferentHere"),
    113: ("CIN", "Reds", "#ATOBTTR"),
    114: ("CLE", "Guardians", "#ForTheLand"),
    115: ("COL", "Rockies", "#Rockies"),
    116: ("DET", "Tigers", "#DetroitRoots"),
    117: ("HOU", "Astros", "#LevelUp"),
    118: ("KC", "Royals", "#TogetherRoyal"),
    119: ("LAD", "Dodgers", "#AlwaysLA"),
    120: ("WSH", "Nationals", "#NATITUDE"),
    121: ("NYM", "Mets", "#LGM"),
    133: ("OAK", "Athletics", "#DrumTogether"),
    134: ("PIT", "Pirates", "#LetsGoBucs"),
    135: ("SD", "Padres", "#TimeToShine"),
    136: ("SEA", "Mariners", "#SeaUsRise"),
    137: ("SF", "Giants", "#SFGameUp"),
    138: ("STL", "Cardinals", "#STLCards"),
    139: ("TB", "Rays", "#RaysUp"),
    140: ("TEX", "Rangers", "#StraightUpTX"),
    141: ("TOR", "Blue Jays", "#NextLevel"),
    142: ("MIN", "Twins", "#MNTwins"),
    143: ("PHI", "Phillies", "#RingTheBell"),
    144: ("ATL", "Braves", "#ForTheA"),
    145: ("CWS", "White Sox", "#ChangeTheGame"),
    146: ("MIA", "Marlins", "#MakeItMiami"),
    147: ("NYY", "Yankees", "#RepBX"),
    158: ("MIL", "Brewers", "#ThisIsMyCrew"),
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
print(
    f'The longest hit streak belongs to {df_streaks["Player"][0]} with a hit streak of {df_streaks["Games"][0]} games'
)


def get_active_game_ids():
    all_game_ids = []
    active_game_ids = []
    for i in range(len(today_schedule)):
        if today_schedule[i]["status"] == "In Progress":
            all_game_ids.append(today_schedule[i]["game_id"])
            active_game_ids.append(today_schedule[i]["game_id"])
        else:
            all_game_ids.append(today_schedule[i]["game_id"])
    return all_game_ids, active_game_ids


# loop through active games
game_ids = get_active_game_ids()[1]
for game in game_ids:
    print(f"scraping game id: {game}")
    url = f"https://statsapi.mlb.com/api/v1/game/{game}/playByPlay"
    res = requests.get(url)
    data = res.json()
    # loop through all plays in this game, looking for a hit
    for i in range(len(data["allPlays"]) - 1):
        try:
            event = data["allPlays"][i]["result"]["event"]
        except:
            continue

        # Continue only for hits
        if (
            event == "Single"
            or event == "Double"
            or event == "Triple"
            or event == "Home Run"
        ):

            # save name of player who got a hit
            name = data["allPlays"][i]["matchup"]["batter"]["fullName"]

            # check if "name" has a hitting streak of > 5 games
            if name in df_streaks["Player"].value_counts():
                hit_streak = (
                    int(
                        df_streaks.loc[(df_streaks["Player"] == name)]["Games"].values[
                            0
                        ]
                    )
                    + 1
                )
                # print out name of player and their qualifying hit streak
                print(
                    f"{name} has a hit, and a qualifying hit streak of {hit_streak} games"
                )

                # check pkl file to see if name has already been tweeted about
                             
                bucket = config.bucket
                key = config.key
                s3 = boto3.resource("s3")
                previous_content = pickle.loads(
                    s3.Bucket(bucket).Object(key).get()["Body"].read()
                )
                try:
                    tweets = previous_content.split(",")
                    print(f"tweets list is: {tweets}")
                except:
                    tweets = []
                    

                # if name hasn't been tweeted about, proceed
                if name not in tweets:
                    if "Jr" in name:
                        last_name = " ".join(name.split()[-2:])
                    else:
                        last_name = name.split()[-1]

                    # identify what team batter is on
                    player_team_id = statsapi.lookup_player(name)[0]["currentTeam"][
                        "id"
                    ]

                    # save details from the hit to variables
                    pitcher_name = data["allPlays"][i]["matchup"]["pitcher"]["fullName"]
                    pitch_type = data["allPlays"][0]["playEvents"][-1]["details"][
                        "type"
                    ]["description"]
                    pitch_speed = data["allPlays"][0]["playEvents"][-1]["pitchData"][
                        "startSpeed"
                    ]

                    # Set emojis
                    # event_emoji
                    if event == "Home Run":
                        event_emoji = "\U0001F4A3\U0001F680"
                    elif event == "Single":
                        event_emoji = "\U00000031\U000020E3"
                    elif event == "Double":
                        event_emoji = "\U0000270C"
                    elif event == "Triple":
                        event_emoji = "\U0001F3C3\U0001F3C3\U0001F3C3"

                    # exit_velo emoji
                    try:
                        exit_velo = data["allPlays"][i]["playEvents"][-1]["hitData"][
                            "launchSpeed"
                        ]
                        # set emoji for exit velocity
                        if exit_velo > 110:
                            exit_velo_emoji = "\U0000203C"
                        elif exit_velo >= 100:
                            exit_velo_emoji = "\U000026A1"
                        elif exit_velo >= 90:
                            exit_velo_emoji = "\U0001F44F"
                        else:
                            exit_velo_emoji = ""
                    except:
                        exit_velo = "Not Recorded"

                    # launch_angle emoji
                    try:
                        launch_angle = data["allPlays"][i]["playEvents"][-1]["hitData"][
                            "launchAngle"
                        ]
                        if 25 <= launch_angle <= 35:
                            launch_angle_emoji = "\U0001F64C"
                        elif launch_angle < 10:
                            launch_angle_emoji = "\U0001F447"
                        else:
                            launch_angle_emoji = ""
                    except:
                        launch_angle_emoji = ""

                    # batting_avg emoji
                    batting_avg = float(
                        df_streaks.loc[(df_streaks["Player"] == name)]["BA"].values[0]
                    )
                    if 0.300 <= batting_avg < 0.400:
                        heat_check_emoji = "\U0001F440"
                    elif 0.400 <= batting_avg < 0.500:
                        heat_check_emoji = "\U0001F525"
                    elif batting_avg >= 0.500:
                        heat_check_emoji = "\U0001F60D"
                    else:
                        heat_check_emoji = ""

                    # Fix batting average to be three significant digits
                    if len(str(batting_avg)) == 4:
                        avg_fixed = str(batting_avg) + "0"
                    elif len(str(batting_avg)) == 3:
                        avg_fixed = str(batting_avg) + "00"
                    else:
                        avg_fixed = batting_avg
                    avg_fixed = str(avg_fixed).lstrip("0")

                    # Send Tweet
                    current_hour = datetime.datetime.now().hour
                    current_time = datetime.datetime.now()

                    if event == "Double":
                        upload_result = api.media_upload(r"utah_two.mp4")
                        text = f"{team_dict[player_team_id][-1]}\n\n{name} hit a {event.lower()}{event_emoji} off of an {pitch_speed} mph {pitch_type.lower()} from {pitcher_name}, and now has a {hit_streak} game hit streak.\n\nExit Velocity: {exit_velo} mph{exit_velo_emoji}\n\nLaunch Angle: {launch_angle} degrees{launch_angle_emoji}\n\n{last_name} is batting {avg_fixed} over this stretch.{heat_check_emoji}"
                        # print('tweet would be fired') # uncomment to debug, comment-out below tweet line
                        try:
                            api.update_status(
                                status=text, media_ids=[upload_result.media_id_string]
                            )
                            print(f"tweet fired for {name} at {current_time}")
                        except:
                            print(f"try/except caught the duplicate tweet for {name}")

                    else:
                        # print('tweet would be fired') #uncomment to debug, and comment below tweet line
                        try:
                            api.update_status(
                                f"{team_dict[player_team_id][-1]}\n\n{name} hit a {event.lower()}{event_emoji} off of an {pitch_speed} mph {pitch_type.lower()} from {pitcher_name}, and now has a {hit_streak} game hit streak.\n\nExit Velocity: {exit_velo} mph{exit_velo_emoji}\n\nLaunch Angle: {launch_angle} degrees{launch_angle_emoji}\n\n{last_name} is batting {avg_fixed} over this stretch.{heat_check_emoji}"
                            )
                            print(f"tweet fired for {name} at {current_time}")
                        except:
                            print(f"try/except caught the duplicate tweet for {name}")

                    # write player's name to s3 bucket to prevent duplicate tweet (line 115 will prevent the double tweet)
                    s3 = boto3.resource("s3")
                    previous_content = pickle.loads(
                        s3.Bucket(bucket).Object(key).get()["Body"].read()
                    )
                    player_name_to_add = pickle.dumps(f"{previous_content},{name}")
                    s3.Object(bucket, key).put(Body=player_name_to_add)
                    break

                else:
                    print(f"{name} already tweeted about")
                    continue

            else:
                # print(f'{name} got a hit, but does not have qualifying hit streak')
                continue
current_time = datetime.datetime.now()
print(f"script finished at {current_time}")


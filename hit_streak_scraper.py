import requests
import datetime
from datetime import date
import pandas as pd

# scrape current hit streak data from baseballmusings.com.
# this function will return a dataframe of all players with active hit streaks of >= 5 games


def scrape_baseball_musings():
    today = date.today()
    day = str(today)[-2:]
    month = str(today)[5:7]
    url = f"https://www.baseballmusings.com/cgi-bin/CurStreak.py?EndDate={month}%2F{day}%2F2022"
    resp = requests.get(url)
    with open("/tmp/test_mlb_longesthitstreak.txt", "wb") as f:
        f.write(resp.content)
    df_streaks = pd.read_html("/tmp/test_mlb_longesthitstreak.txt")
    df_streaks = pd.DataFrame(df_streaks[1])
    return df_streaks


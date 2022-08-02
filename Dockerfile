FROM python:latest

WORKDIR /usr/app/src

COPY config.py utah_two.mp4 hit_streak_bot.py hit_streak_scraper.py requirements.txt ./

RUN pip install MLB-StatsAPI

RUN pip install tweepy

RUN pip install pandas

RUN pip install lxml

RUN pip install numpy

RUN pip install requests

RUN pip install DateTime

RUN pip install schedule

RUN pip install times

CMD ["python", "./hit_streak_bot.py"]


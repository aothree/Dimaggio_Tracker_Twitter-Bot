FROM python:latest

WORKDIR /usr/app/src/

COPY dimaggio_twitter_bot.py config.py utah_two.mp4 hit_streak_scraper.py requirements.txt ./

RUN pip install MLB-StatsAPI

RUN pip install tweepy

RUN pip install pandas

RUN pip install lxml

RUN pip install numpy

RUN pip install requests

RUN pip install DateTime

RUN pip install schedule

RUN pip install times

RUN pip install boto3

RUN pip install pickle5

CMD ["python", "./dimaggio_twitter_bot.py"]


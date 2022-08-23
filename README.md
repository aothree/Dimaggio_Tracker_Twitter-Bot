# Dimaggio_Tracker

Twitter Bot tracking all active MLB hit-streaks >= 5 games.  

Tweets are automatically sent out when one of these players gets a hit to extend their hit-streak.  

Check it out and follow if you'd like! https://twitter.com/DiMaggioTracker


-------------

## General Method

1. Scrape hit-streak data from baseballmusings.com, 1x/day.

2. Write script that uses MLB Stats API to scrape active mlb games' play-by-play data, looking for hits that qualify as part of a 5+ game hit-streak.  When a qualifying hit is found, a tweet is automatically sent out by @Dimaggio_Tracker.

3. Store `.py` script in a Docker image

4. Upload image to AWS' Elastic Container Registry.

5. Create an AWS Lambda Function that runs the script whenever live baseball games are happening.

6. De-bug, de-bug, de-bug, and then de-bug some more.  
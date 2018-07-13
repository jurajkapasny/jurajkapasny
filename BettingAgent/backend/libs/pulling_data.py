
# coding: utf-8

# In[21]:


import pandas as pd
import numpy as np

import itertools
import csv
import re
from SportsFeedAPI.api import *


# In[22]:


config = MsfLib(version="1.0")
storage = FeedStorageMethod(config)


# In[23]:


class PullData:
    
    def __init__(self, sport, season, season_type, date, output_type):
    
        self.sport = sport
        self.season = season
        self.season_type = season_type
        self.date = date
        self.output_type = output_type
    
        self.feed = Feed(config, 
                    sport=self.sport, 
                    season=self.season, 
                    season_type=self.season_type, 
                    date=self.date, 
                    output_type=self.output_type)

        self.feed.set_store(storage)

        
    def pull_all(self):
        df_cum_player_stats = self.pull_cum_player_stats(self.feed, self.date, self.season, self.season_type)
        df_roster_players = self.pull_roster_players(self.feed, self.date, self.season, self.season_type)
        df_player_injuries = self.pull_player_injuries(self.feed, self.date, self.season, self.season_type)
        df_daily_player_stats = self.pull_daily_player_stats(self.feed, self.date, self.season, self.season_type)

        #TODO - pull box score and play by play
        
        return  (
                df_cum_player_stats,
                df_roster_players,
                df_player_injuries,
                df_daily_player_stats
        )
    
    @staticmethod
    def pull_cum_player_stats(feed, date, season, season_type):
        feed.cum_player_stats()
        path_data = "../../data/nba-cumulative_player_stats-" + date + "-" + season +                    "-" + season_type + ".csv"
    #     print path_data

        data = []
        i = 0
        with open(path_data, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if i == 0:
                    names = re.sub("#","",row[0]).split(',')
                    #print row
                else:
                    data.append(re.split(''',(?=(?:[^"]|'[^']*'|"[^"]*")*$)''', re.sub("#","",row[0])))
                    #parsing at each , except when ","
                i = i+1
        df = pd.DataFrame(data, columns = names)

        return df
    
    @staticmethod
    def pull_roster_players(feed, date, season, season_type):
        feed.roster()
        path_data = "../../data/nba-roster_players-" + date + "-" + season +                    "-" + season_type + ".csv"
    #     print path_data

        data = []
        i = 0
        with open(path_data, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if i == 0:
                    names = re.sub("#","",row[0]).split(',')
                    #print row
                else:
                    data.append(re.split(''',(?=(?:[^"]|'[^']*'|"[^"]*")*$)''', re.sub("#","",row[0])))
                    #parsing at each , except when ","
                i = i+1
        df = pd.DataFrame(data, columns = names)

        return df

    @staticmethod
    def pull_player_injuries(feed, date, season, season_type):
        feed.player_injuries()
        path_data = "../../data/nba-player_injuries-" + date + "-" + season +                    "-" + season_type + ".csv"
    #     print path_data

        data = []
        i = 0
        with open(path_data, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if i == 0:
                    names = re.sub("#","",row[0]).split(',')
                    #print row
                else:
                    data.append(re.split(''',(?=(?:[^"]|'[^']*'|"[^"]*")*$)''', re.sub("#","",row[0])))
                    #parsing at each , except when ","
                i = i+1
        df = pd.DataFrame(data, columns = names)

        return df

    @staticmethod
    def pull_daily_player_stats(feed, date, season, season_type):
        feed.daily_player_stats()
        path_data = "../../data/nba-daily_player_stats-" + date + "-" + season +                    "-" + season_type + ".csv"
    #     print path_data

        data = []
        i = 0
        with open(path_data, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if i == 0:
                    names = re.sub("#","",row[0]).split(',')
                    #print row
                else:
                    data.append(re.split(''',(?=(?:[^"]|[^]*|"[^"]*")*$)''', re.sub("#","",row[0])))
                    #parsing at each , except when ","
                i = i+1
        df = pd.DataFrame(data, columns = names)

        return df


# In[19]:


# pullData = PullData(config, storage, "nba", "2016-2017", "regular", "20170120", "csv")


# In[20]:


# (
# df_cum_player_stats,
# df_roster_players,
# df_player_injuries,
# df_daily_player_stats) = pullData.pull_all()


# In[57]:


# df_roster_players


# In[24]:


# df_daily_player_stats


# In[64]:


# #BoxScore and PlayByPlay(only for json)
# feed.boxscore("CLE","IND")


# In[63]:


# feed.play_by_play("CLE","IND")


# In[62]:


# file = "./results/nba-game_playbyplay-20170215-2016-2017-regular-20170215-IND-CLE.json"
# with open(file) as f:
#     PlayByPlay_dict = json.loads(''.join(f))


# In[15]:


# PlayByPlay_dict["gameplaybyplay"]["plays"]["play"]


# In[61]:


# play_by_play = {}
# play_by_play["time"] = []
# play_by_play["quarter"] = []
# play_by_play["play_type"] = []
# j = 0
# for play in PlayByPlay_dict["gameplaybyplay"]["plays"]["play"]:
#     keys = list(play.keys())
#     play_by_play["quarter"].append(play["quarter"])
#     keys.remove('quarter')
#     play_by_play["time"].append(play["time"])
#     keys.remove('time')
#     play_by_play["play_type"].append(keys[0])
#     j += 1

# df_play_by_play = pd.DataFrame(play_by_play)
    
    


# In[58]:


# df_play_by_play.head()


# In[59]:


# set(df_play_by_play.play_type)


# In[60]:


# PlayByPlay_dict["gameplaybyplay"]["plays"]


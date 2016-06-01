
# coding: utf-8

# In[1]:

import tweepy
import json
import numpy as np
import pandas as pd
import string
import time
import pickle
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment 
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
from matplotlib import pyplot as plt
import matplotlib as mpl
from prettyplotlib.utils import remove_chartjunk

#%pylab inline


consumer_key = "<consumer-key>"
consumer_secret = "<consumer-secret>"
access_token = "<access-token>"
access_token_secret = "<access-token-secret>"
NUM_TWEETS = float("Inf") #max number of tweets to pull
keywords =['keywords', 'to', 'search']
tweet_path = '<path-to-save-tweets>'


# In[2]:

class StdOutListener(tweepy.streaming.StreamListener):
    """
    Child class to tweety StreamListener, filtering 
    and processing and collecting the tweets on the fly
    """
    def __init__(self, tweet_path, api=None):
        super(StdOutListener, self).__init__()
        self.num_tweets = 0
        self.collection = {}
        self.tweet_path = tweet_path #path to save tweets
    
    def on_data(self, data):
        """
        class method to handle incoming data
        
        input:
            data - JSON (tweet)
        """
        data = json.loads(data)
        if self.num_tweets > NUM_TWEETS:
            return False
        try:
            self.process_raw_tweet(data)
            self.num_tweets += 1
        
        except Exception as e:
            print e
            return True        
        
        return True
    
    def on_exception(self, status):
        """
        Class method to handle API exceptions
        """
        print "exception raise:"
        print status
    
    def on_error(self, status):
        """
        Class method to handle API errors
        """
        print status
        
    def process_raw_tweet(self, data):
        """
        Class method to process single tweet
        
        input:
            data - JSON (tweet)
        """
        record = {}
        try:        
            if data["coordinates"] is not None: #specific location
                #print "Specific location"
                record["coordinates_long"] = data["coordinates"]["coordinates"][0]
                record["coordinates_lat"] = data["coordinates"]["coordinates"][1]
                record["coordinates_type"] = "from_coordinates"
            elif data["place"]["bounding_box"] is not None: #only bounding box available
                #print "Bounding box"
                this_coor = data["place"]["bounding_box"]["coordinates"][0]
                avg_long = np.mean([i for i,_ in this_coor]) #get middle of bounding box
                avg_lat = np.mean([j for _,j in this_coor])
                try:
                    record["place_name"] = data["place"]["name"]
                except:
                    record["place_name"] = "no_name"
                record["coordinates_lat"] = avg_lat
                record["coordinates_long"] = avg_long
                record["coordinates_type"] = "from_place"
            else:
                return True #if no location, just continue
            
            record["text"] = data["text"]
            record["favorite_count"] = data["favorite_count"]
            record["retweet_count"] = data["retweet_count"]
            record["created_at"] = data["created_at"]
            
            #write to file
            with open(self.tweet_path + "tweets.txt", 'a') as fp:
                json.dump(record, fp)
        except:
            return True

        return True


# In[41]:

class TweetStream():
    """
    Class to handle the stream of tweets
    """
    def __init__(self, 
                 consumer_key,
                 consumer_secret,
                 access_token, 
                 access_token_secret,
                 keywords,
                 tweet_path):
        #keywords to filter by
        self.keywords = keywords
        #authentication
        self.twitter_api = StdOutListener(tweet_path = tweet_path)
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        #set path to save tweets
        self.tweet_path = tweet_path
        
    def get_stream(self):
        """
        Class method to activate the Twitter stream API
        """
        self.stream = tweepy.Stream(self.auth, self.twitter_api, timeout = 100)
        
    def filter_stream(self):
        """
        Class method to filter the stream according to supplied keywords
        """
        self.stream.filter(track = self.keywords)
        
    def pull_tweets(self):
        """
        Class method to pull stream of tweets
        includes bells and whistles to keep it going in case of crash
        Should be able to run indefinitely!!
        """
        while True:
            self.get_stream()
    
            try:
                #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
                self.filter_stream()

            except tweepy.TweepError:
                time.sleep(60 * 15)
                continue
            except Exception, e:
                print "Error. Restarting Stream.... Error: "
                print e.__doc__
                print e.message

class TweetSentiment:
    """
    Class to calculate and plot tweet sentiments
    
    supports:
        hexbin map plot
        scatter map plot
        distribution histogram of sentiments
        
    """
    def __init__(self, tweet_path):
        self.read_tweets_from_file(tweet_path)
        self.process_tweets()
        self.unique_locations()
        self.pickle(tweet_path)
    
    def read_tweets_from_file(self, path):
        """
        Class method to read and process tweets from file
        """
        self.data = {}
        ind = 0
        with open(path + "tweets.txt") as fp:
            for line in fp.readlines():
                line = line.replace("|||", "")
                line = line.replace("}{", "}|||{")
                th_data = line.split("|||")
                for d in th_data:
                    self.data[ind] = eval(d)
                    ind += 1
    @staticmethod   
    def get_sentiment_single(tweet):
        """
        Static helper method to get sentiment for one tweet
        Uses vaderSentiment library
        """
        tweet = ''.join(filter(lambda x: x in string.printable, tweet))
        sent = vaderSentiment(tweet)
        return sent["compound"]

    def process_tweets(self):
        """
        Class method to process tweets:
            *calculates sentiments for all tweets in collection
            *formats timestamps
            *records geo coordinates
        """
        self.data_pd = (pd
                        .DataFrame(self.data)
                        .transpose())
        self.data_pd["sentiment"] = (self
                                     .data_pd
                                     .apply(lambda tweet: self.get_sentiment_single(tweet.text),
                                            axis = 1))
        self.data_pd = self.data_pd.ix[self.data_pd.sentiment != 0]
        #data formats
        self.data_pd["timestamp"] = (self
                                     .data_pd
                                     .apply(lambda x: (time
                                                        .mktime(time
                                                                .strptime(x
                                                                          .created_at,
                                                                          "%a %b %d %H:%M:%S +0000 %Y"))), 
                                             axis = 1))
        self.data_pd.sort_values(by = ["coordinates_lat", "coordinates_long"],
                          inplace = True)
        self.lats = (np
                     .array(self
                            .data_pd
                            .coordinates_lat
                            .values,
                            dtype="float64"))
        self.lons = (np
                     .array(self
                            .data_pd
                            .coordinates_long
                            .values, 
                            dtype="float64"))
        self.sents = (np.array(self
                               .data_pd
                               .sentiment
                               .values,
                               dtype="float64"))
            
    def pickle(self, tweet_path):
        """
        class method to save class to pickle
        """
        f = file(tweet_path + "sents.pickle", "wb")
        pickle.dump(self, f)
        f.close()
            
    def plot_sents_scatter(self,
                           projection = "merc",
                           lat_0=0, 
                           lon_0=0,
                           llcrnrlat=-65,
                           llcrnrlon=-178,
                           urcrnrlat=80,
                           urcrnrlon=178,
                           area_thresh=10000,
                           resolution = 'i',
                           point_size=None,
                           cmap = "coolwarm"):
        """
        Class method to plot scatter on a map
        
        Inputs:
            any for Basemap package
            point_size - int, size of point
            cmap - string, colour map to user (matplotlib)
            
        Return:
            plot.show()
        """
        # create figure and axes instances
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_axes([0.1,0.1,0.8,0.8])

        #colourmap
        norm = mpl.colors.Normalize(vmin=-1, vmax=1)
        m = cm.ScalarMappable(norm=norm, cmap=cmap)
        
        #get map object
        my_map = self.get_map(projection,
                              lat_0, 
                              lon_0,
                              llcrnrlat,
                              llcrnrlon,
                              urcrnrlat,
                              urcrnrlon,
                              area_thresh,
                              resolution)
        
        #setting point size
        if point_size is None:
            s = urcrnrlon - llcrnrlon #default proportional to size of map
        else:
            s = point_size
        
        #transform into projection
        x,y = my_map(self.lons, self.lats)
        sc = my_map.scatter(x, 
                       y,
                       marker = "o", 
                       s = s,
                       c = m.to_rgba(self.sents),
                       alpha = 0.7)
        # add title
        plt.title("Sentiment map")
        plt.show()
    
    
    def plot_sents_hist(self, cmap="coolwarm", bins = 40):
        """
        Class method to plot histogram of twitter sentiments
        
        Input:
            cmap - str, colormap to user (matplotlib supported, default coolwarm)
            bins - int, number of bins for the histogram (default 40)
            
        Return:
            plot.show()
        """
        #colourmap
        norm = mpl.colors.Normalize(vmin=-1, vmax=1)
        m = cm.ScalarMappable(norm=norm, cmap=cmap)

        fig, ax = plt.subplots(1)

        patches = ax.hist(self.sents, bins = bins, range = [-1.,1.])
        remove_chartjunk(ax,
                         ['top', 'right'],
                         grid='y',
                         show_ticks=False)


        for c, p in zip(patches[1], patches[2]):
            plt.setp(p, 'facecolor', m.to_rgba(c))

        plt.xlabel("Sentiment value")
        plt.ylabel("Number of tweets")
        plt.title("Sentiment distribution")
        plt.show()
        
    def plot_sents_hexbinmap(self,
                             gridsize=500,
                             projection="merc",
                             lat_0=0, 
                             lon_0=0,
                             llcrnrlat=-65,
                             llcrnrlon=-178,
                             urcrnrlat=80,    
                             urcrnrlon=178,
                             area_thresh=10000,
                             resolution="i",
                             cmap="coolwarm"):
        """
        Class method to plot hexbin map of tweet sentiments
        
        Input:
            any from Basemap
            gridsize - int, size of the grid (default 500)
            cmap - str, colormap to use (matplotlib supported, default coolwarm)
            
        Return:
            plot.show()
        """
       
        #get map object
        my_map = self.get_map(projection,
                              lat_0, 
                              lon_0,
                              llcrnrlat,
                              llcrnrlon,
                              urcrnrlat,
                              urcrnrlon,
                              area_thresh,
                              resolution)
        
        x,y = my_map(self.lons, self.lats)
        my_map.hexbin(x,
                      y, 
                      {"gridsize": gridsize,
                       "C" : self.sents, 
                       "reduce_C_function" : np.median,
                       "cmap" : cmap})

        plt.show()
        
    def unique_locations(self):
        """
        class method to get unique set of locations in tweets
        """
        result_lats = np.unique(self.lats)
        result_lons = np.empty(result_lats.shape)
        result_sents = np.empty(result_lats.shape)

        for i, lat in enumerate(result_lats):
            result_sents[i] = np.median(self.sents[self.lats == lat])
            result_lons[i] = np.median(self.lons[self.lats == lat])

        result_lons_f = np.unique(result_lons)
        result_lats_f = np.empty(result_lons_f.shape)
        result_sents_f = np.empty(result_lons_f.shape)

        for i, lon in enumerate(result_lons_f):
            result_sents_f[i] = np.median(result_sents[result_lons == lon])
            result_lats_f[i] = np.median(result_lats[result_lons == lon])

        self.lons = result_lons_f
        self.lats = result_lats_f
        self.sents = result_sents_f
        
    @staticmethod
    def get_map(projection='merc',
                lat_0=0, 
                lon_0=0,
                llcrnrlat=-65,
                llcrnrlon=-178,
                urcrnrlat=80,
                urcrnrlon=178,
                area_thresh=10000,
                resolution='i'):
        """
        Static method to get Basemap map object with parameters
        
        Input:
            any from Basemap
            
        Return:
            Basemap map object
        """
        # create polar stereographic Basemap instance.
        my_map = Basemap(projection='merc',
                         lat_0=lat_0, 
                         lon_0=lon_0,
                         llcrnrlat = llcrnrlat, 
                         llcrnrlon = llcrnrlon,
                         urcrnrlat = urcrnrlat, 
                         urcrnrlon = urcrnrlon,
                         resolution='i',
                         area_thresh=area_thresh)

        my_map.drawcoastlines()
        my_map.drawcountries()
        return my_map


# In[ ]:

# ts = TweetSentiment(tweet_path)
# ts.plot_sents_scatter(point_size = 10)
# ts.plot_sents_hist()
# ts.plot_sents_hexbinmap()


# In[ ]:

if __name__ == '__main__':
    try:
        #This handles Twitter authetification and the connection to Twitter Streaming API
        twitter_stream = TweetStream(consumer_key,
                                     consumer_secret,
                                     access_token, 
                                     access_token_secret,
                                     keywords,
                                     tweet_path)
        twitter_stream.pull_tweets()
    except:
        raise "TwitterAPI connection crashed"


# In[ ]:

#TODO add colorbars to map plots


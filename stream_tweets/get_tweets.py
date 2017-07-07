
# coding: utf-8

# In[1]:

#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
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
            try: # If coordinates are available
                if data["coordinates"] is not None: #specific location
                    #print "Specific location"
                    record["coordinates_long"] = data["coordinates"]["coordinates"][0]
                    record["coordinates_lat"] = data["coordinates"]["coordinates"][1]
                    record["coordinates_type"] = "from_coordinates"
            except: 
                pass
            # this is always available
            record["text"] = data["text"]
            record["favorite_count"] = data["favorite_count"]
            record["retweet_count"] = data["retweet_count"]
            record["created_at"] = data["created_at"]
            record["language"] = data["lang"]
            
            #write to file
            with open(self.tweet_path + "tweets.txt", 'a') as fp:
                json.dump(record, fp)
        except:
            return True

        return True


# In[2]:

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
        self.stream = tweepy.Stream(self.auth, self.twitter_api, timeout = 5)
        
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
                time.sleep(1)
                continue
            except Exception, e:
                print "Error. Restarting Stream.... Error: "
                print e.__doc__
                print e.message


# In[3]:

keywords = ["startupchile","#startupchile","@startupchile"]
access_token = "532638082-iNySbHCk2edMlXj2pVGBXYyazAiL0AI8DkXPUgC5"
access_token_secret = "IjRJ8xxHJjjO3mCHDtort52tqXnbsa5UsdA96UDfMsSC1"
consumer_key = "lqSn67SkXzUqxTS3WBTeTPaQN"
consumer_secret = "d6FKfgJeAPFfkBPprxOrA9Dlm3Ls2UEb0d7H1Oljh0d3mZdYK0"
tweet_path = '/Users/jurajkapasny/Data/StartupChile/'
NUM_TWEETS = float("Inf") #max number of tweets to pull
if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    twitter_stream = TweetStream(consumer_key,
                                 consumer_secret,
                                 access_token, 
                                 access_token_secret,
                                 keywords,
                                 tweet_path)
    twitter_stream.pull_tweets()
#     except:
#         print "TwitterAPI connection crashed"


# In[ ]:

#Start-Up Chile


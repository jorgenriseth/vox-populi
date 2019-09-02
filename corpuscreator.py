import os
import tweepy
import json

from utils import json_dump_line, get_tweet_auth

class CorpusCreator:
    """
    Class for creating corpus structure and loading tweets
    using tweepy.
    
    Structure:
    -> corpus
    
    ----> screen_name1
    ------> tweet_id1.txt
    ------> tweet_id2.txt
    
    ----> screen_name2
    ------> tweet_id1.txt
    ------> tweet_id2.txt
    .
    .
    
    """
    
    def __init__(self, user_dict=None, rel_path='./',
                rate_limit_wait=True):
        
        # Get an API-object authorized from 'credentials.txt'
        auth = get_tweet_auth()
        self.api = tweepy.API(auth,
                              wait_on_rate_limit=rate_limit_wait,
                              wait_on_rate_limit_notify=rate_limit_wait)
        
        self.root = rel_path + 'corpus/'
        
        # Load mp-file from directory
        if user_dict is None:
            with open('mps.json') as f:
                self.users = json.load(f)
        else:
            self.users = user_dict
        
        # Create root filesystem
        try:
            os.mkdir(self.root)
            print('Directory "corpus created.')
        except:
            print('Directory "corpus" already exists.')
            
        
            
    def load_tweets(self, max_items=10000):
        """
        For all users in self.users, get [max_items] tweets and
        save each to separate files. 
        """
        for name, info in self.users.items():
            try:
                print(f'Reading tweets from {name}')
                user = info['screen_name']
                curs = tweepy.Cursor(self.api.user_timeline,
                                     screen_name=user,
                                     count=200).items(max_items)

                filename = name.lower().replace(' ', '')
                with open(self.root + filename + '.jsonl', 'w') as f:
                    for status in curs:
                        tweet = status._json
                        json_dump_line(tweet, f)
            except tweepy.TweepError as exc:
                print(exc)
                os.remove(self.root + filename + '.jsonl')

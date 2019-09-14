import os
import sys
import tweepy
import json

class CorpusCreator:
    """
    Class for creating corpus structure and loading tweets
    using tweepy.
    
    Structure:
    -> corpus
    
    ---> party1
    -----> user11
    -----> user12
    -----> user13
    
    ---> party2
    -----> user21
    -----> user22
    .
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
        assert type(user_dict) in (str, dict) or user_dict is None,"User_dict wrong format"
        if user_dict is None:
            user_dict = 'mps.json'
            
        if type(user_dict) is str:
            with open(user_dict) as f:
                self.users = json.load(f)
                
        elif type(user_dict) is dict:
            self.users = user_dict
        
        # Create root filesystem
        try:
            os.mkdir(self.root)
            print('Directory "corpus created.')
            print()
        except:
            print('Directory "corpus" already exists.')
            print()
            
        
            
    def load_tweets(self, max_items=10000, user=None):
        """
        For all users in self.users, get [max_items] tweets and
        save each to separate files. 
        """
        for name, info in self.users.items():
            try:
                os.mkdir(self.root + info['party'].lower().replace(' ', '_'))
            except FileExistsError:
                pass
            
            filepath = self.root + info['party'].lower().replace(' ', '_')
            filepath = filepath + '/' + name.lower().replace(' ', '')
            try:
                print(f'Reading tweets from {name}')
                user = info['screen_name']
                curs = tweepy.Cursor(self.api.user_timeline,
                                     screen_name=user,
                                     count=200,
                                     tweet_mode="extended"
                                     ).items(max_items)

                with open(filepath + '.jsonl', 'w') as f:
                    for status in curs:
                        tweet = status._json
                        json_dump_line(tweet, f)
                        
            except tweepy.TweepError as exc:
                print(exc)
                os.remove(filepath + '.jsonl')

                
def get_tweet_auth(auth_file='credentials.txt'):
    """
    Get tweepy oauth object given a credentials-file, formatted
    as a nltk.twitter-creds file.
    """
    keys = []
    
    # Open credentials-file
    with open(auth_file, 'r') as f:
        for line in f:
            # Read only key/token
            token = line.split('=')[-1].rstrip('\n')
            
            # Add token to keys-list
            if token is not '':
                keys.append(line.split('=')[-1].rstrip('\n'))
                
    auth = tweepy.OAuthHandler(*keys[:2])
    auth.set_access_token(*keys[2:])
    return auth


def json_dump_line(json_object, file_object):
    """
    Dumps a dictionay json_object to file_object, adding 
    a trailing newline, hence creating a json line format.
    """
    json.dump(json_object, file_object)
    file_object.write('\n')

if __name__ == '__main__':
    number_of_tweets = int(input("Number of tweets per user:"))

    # Ensure that the argument is a positive integer.
    assert number_of_tweets > 0, "Number of tweets must be a positive integer"

    # Create MP-list and run corpuscreator
    if not os.path.isfile('mps_test.json'):
        create_user_list()

    corpus_creator = CorpusCreator(user_dict='mps_test.json')
    corpus_creator.load_tweets(max_items=number_of_tweets)

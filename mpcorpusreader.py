import json
import pandas as pd

from nltk.tokenize import TweetTokenizer
from nltk.corpus.reader import TwitterCorpusReader

class MPTweetCorpusReader(TwitterCorpusReader):
    """
    Class cerate specifically for ease of use in text clustering of the 
    British Member of Parliament tweets.
    """
    
    def __init__(self, root, fileids=None, word_tokenizer=TweetTokenizer(),
                 encoding='utf-8', create_df=False):
        TwitterCorpusReader.__init__(self, root, fileids, word_tokenizer,
                                     encoding)

        self.parties = list(set([fileid.split('/')[0] for fileid in self.fileids()]))
        self.users = [fileid.split('/')[1].split('.')[0] for fileid in self.fileids()]
        
        self.num_tweets = len(self.strings())
        self.num_parties = len(self.parties)
        self.num_users = len(self.users)
        
        
        with open(self.root + '../mps.json') as f:
            self._mp_dict = json.load(f)
        
        
        self.df_savepath = self.root + 'tweet_df.pkl'
        
        if create_df:
            print('Building tweet dataframe.')
            self._build_dataframe()
            print('Tweet dataframe built.')
            print()
        
        else:
            try:
                print("Loading tweet dataframe.")
                self.df = pd.read_pickle(self.df_savepath)
                print("Tweet dataframe loaded.")
                print()
            
            except OSError as exc:
                self.df = None
                
                print('OSError: ' + exc)
                print("No dataframe created/loaded.")
                print()
    
    def strings(self, fileids=None):
        """
        Returns only the text content of Tweets in the file(s)
        :return: the given file(s) as a list of Tweets.
        :rtype: list(str)
        """
        fulltweets = self.docs(fileids)
        tweets = []
        for jsono in fulltweets:
            try:
                text = jsono["full_text"]
                if isinstance(text, bytes):
                    text = text.decode(self.encoding)
                tweets.append(text)
            except KeyError:
                pass
        return tweets
                
    def _build_dataframe(self):
        self.df = pd.DataFrame(columns=['user', 'party', 'userid', 'text'])
        i = -1    
        for user, info in self._mp_dict.items():
            # Get filepath for users tweet
            user_fileids = (info['party'].lower().replace(' ', '_') + '/' 
                            + user.lower().replace(' ', '') + '.jsonl')

            try:
                user_tweets = self.strings(user_fileids)

                for string in user_tweets:
                    i += 1
                    self.df.loc[i] = [user, info['party'], info['screen_name'], string]

            except OSError:
                # File doesn't exists, probably due to locked twitter profile.
                pass

            
    def to_dataframe(self, samples='tweet', savename=None):
        """
        samples = string: {'tweet', 'user', 'party'}
        
        Create a dataframe where each row reperesnts one tweet, and stores 
        as a member variable. If samples is 'user' or 'party', it will return 
        a dataframe for which all tweets belonging to a single user/party is 
        concatenated into one. 
        """
        assert samples in ("tweet", "user", "party"), "Invalid argument [samples]:" + str(samples)
        
        # Create base dataframe.
        if samples == "tweet":
            return self.df
            
        # Create "lower resolution" dataframes if necessary
        if samples in ("user", "party"):
            
            df_by_user = pd.DataFrame(columns=['user', 'party', 'text'])
            
            i = -1
            for user, info in self._mp_dict.items():
                # Concatenate all tweets from user into one string.
                tweets = ' '.join(list(self.df.loc[self.df['user'] == user]['text']))
                
                if tweets != '':
                    i += 1
                    df_by_user.loc[i] = [user, info['party'], tweets]
                    
            # Let name of mp/user be index of dataframe
            df_by_user.set_index('user', inplace=True)
            
            if samples == "party":
                df_by_party = pd.DataFrame(columns=['party', 'text'])
                
                i = -1
                for party in df_by_user['party'].unique():
                    # Concatenate tweets from all users in party into single string
                    tweets = ' '.join(list(df_by_user.loc[df_by_user['party'] == party]['text']))
                    
                    if tweets != '':
                        i += 1
                        df_by_party.loc[i] = [party, tweets]
                        
                df_by_party.set_index('party', inplace=True)
                        
                if savename is not None:
                    df_by_party.to_pickle(self.root + savename)
                return df_by_party
            
            if savename is not None:
                df_by_user.to_pickle(self.root + savename)
            return df_by_user
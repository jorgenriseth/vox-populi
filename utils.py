"""
Miscellaneous helper functions
"""
import tweepy
import json
import requests
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup




"""
Printing Macros
"""
class print_color:
    PURPLE= '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREY = '\033[97m'
    BLACK = '\033[98m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
party_color_map = {
    'Conservative': print_color.BLUE,
    'Democratic Unionist Party': print_color.YELLOW,
    'Green Party': print_color.GREEN,
    'Independent': print_color.GREY,
    'Labour': print_color.RED,
    'Liberal Democrat': print_color.PURPLE,
    'Plaid Cymru': print_color.DARKCYAN,
    'Scottish National Party': print_color.GREY,
    'Sinn Fein': print_color.CYAN,
    'The Independent Group': print_color.BLACK
}



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
    

def user_id_correction(erratafile='user-errata.txt',
                       user_file='mps.json'):
    """
    Fixes errors in user_file, using information stored in erratafile
    """
    # Create dictionary with errata[wrong-id] = errata[righ-id]
    with open(erratafile, 'r') as f:
        errata = {}

        for line in f:
            line = line.rstrip('\n')
            errata[line.split('=')[0]] = line.split('=')[1]

    # Load dictironary to be corrected
    with open(user_file, 'r') as f:
        user_dict = json.load(f)
    
    
    # Correct the entries in the user-file
    for wrong_id, right_id in errata.items():
        for name, info in user_dict.items():
            if info["screen_name"] == wrong_id:
                print()
                print('Correction')
                print('Old: ', user_dict[name])
                user_dict[name]["screen_name"] = right_id
                user_dict[name]["url"] = info["url"][:-len(wrong_id)] + right_id
                print('New: ', user_dict[name])
                print()

    # Save corrected dictionary to json.
    with open(user_file, 'w') as f:
        json.dump(user_dict, f)


def create_user_list(filename='mps.json', errata='user-errata.txt'):
    """
    Retrieves list of MP's on twitter, and store their username,
    political party, and twitter profile url in a json file,
    their full names as keywords.
    """

    url = "https://www.mpsontwitter.co.uk/list"
    data = requests.get(url)

    html = BeautifulSoup(data.text, 'html.parser')
    table = html.select("tbody", id='mp_wrapper')[1]

    mp_dict = {}
    for line in table.select('tr'):
        name = line.select('td')[2].get_text().strip()
        party = ' '.join(line.td['class'])
        twitter_id = line.a.get_text()[1:]
        url = line.a['href']
            
        mp_dict[name] = {
            "party": party,
            "screen_name": twitter_id,
            "url": "https://twitter.com/" + twitter_id
        }

    with open(filename, 'w') as f:
        json.dump(mp_dict, f)
        
    if errata is not None:
        user_id_correction(erratafile=errata, user_file=filename)
        
    print(f'MPs on Twitter stored in {filename}')
    
    
def visualize(df, color_by='label', num_samples='all', marker_labels=True,
              ax=None, savename=None):
    """
    2D projection plot of all (or a subset of) points in df after 
    performed clustering. The points color is specified by the value
    in the "color_by"-argument. 
    
    If num_samples is an integer, it will only plot num_samples data points
    randomly sampled from the available data. This might be useful for a high
    number of data points.
    
    marker_labels specifies whether the points should be plotted alongside the 
    points index value. (typically user or party).
    
    If savename is specified, the resulting figure is saved to disk. 
    """
    if num_samples is not 'all':
        groups = df.sample(num_samples).groupby(color_by)
    else:
        groups = df.groupby(color_by)
        
    if ax is None:
        fig, ax = plt.subplots(figsize=(16, 12)) # set size
        
    ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling
    
    # Loop through groups and plot by color
    for color, group in groups:
        ax.plot(group.posx, group.posy, marker='o', ms=6,
                ls='', label=color)
        
        # Configure axes
        ax.set_aspect('auto')
        ax.tick_params(
            axis= 'x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off')
        
        ax.tick_params(
            axis= 'y',         # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left='off',        # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelleft='off')
        
        ax.legend(numpoints=1, loc=2)
        
        if marker_labels:
            for i in range(len(group)):
                ax.text(group.iloc[i]['posx'] - 1e-2, group.iloc[i]['posy'] + 8e-3,
                        group.index[i], size=8)
        
    if savename is not None:
        plt.savefig(savename, dpi=200)
            
    return ax




def cluster_information(df, vectorizer, clusterer, num_words=15,
                        show_users=True):
    """
    Print clusters, and most used features per cluster.
    """
    # Ensure that model is allready fitted
    assert hasattr(clusterer, 'cluster_centers_'), "Need to fit clusterer first."
    
    terms = vectorizer.get_feature_names()
    order_centroids = clusterer.cluster_centers_.argsort()[:, ::-1]
    num_clusters = clusterer.get_params()['n_clusters']

    for i in range(num_clusters):
        print()
        print('=' * 80)
        print(print_color.BOLD + "Cluster %d:"  % i + print_color.END,
              end='')

        for ind in order_centroids[i, :15]:
            print('%s, ' % terms[ind], end='')

        print()
        
        if show_users:
            print('-' * 50)
            for user in df.loc[df['label'] == i].index:
                party = df.loc[user]['party']
                print(user + '(' + party_color_map[party] + party + '), '
                      + print_color.END, end='')
            print()
        print('=' * 80)

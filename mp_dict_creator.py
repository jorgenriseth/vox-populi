import requests
import json

from bs4 import BeautifulSoup

def create_user_list(filename='mps.json', errata=None):
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
    

if __name__ == '__main__':
    create_user_list(errata='user-errata.txt')
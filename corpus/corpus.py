import sys
import os

from utils import create_user_list
from corpuscreator import CorpusCreator


if __name__ == '__main__':
    # Ensure that max number of tweets is passed as argument.
    if len(sys.argv) != 2:
        print("Invalid arguments. Expects:")
        print("python corpus [max_tweets_per_user]")
        sys.exit()
    
    number_of_tweets = int(sys.argv[1])
    
    # Ensure that the argument is a positive integer.
    assert number_of_tweets > 0, "Number of tweets must be a positive integer"
    
    # Create MP-list and run corpuscreator
    if not os.path.isfile('mps.json'):
        create_user_list()

    corpus_creator = CorpusCreator()
    corpus_creator.load_tweets(max_items=number_of_tweets)
    
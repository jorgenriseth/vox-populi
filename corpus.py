import sys

from utils import create_user_list
from corpuscreator import CorpusCreator


if __name__ == '__main__':
    # Ensure that max number of tweets is passed as argument.
    if len(sys.argv) != 2:
        print("Invalid arguments. Expects:")
        print("python corpus [max_tweets_per_user]")
        sys.exit()
    
    number_of_tweets = sys.argv[1]
    
    # Ensure that the argument is a positive integer.
    arg_correct = type(number_of_tweets) and number_of_tweets > 0:
    assert type(number_of_tweets) == int, "Number of tweets must be a positive integer"
    
    # Create MP-list and run corpuscreator
    create_user_list()
    corpus_creator = CorpusCreator()
    corpus_creator.load_tweets(max_items=number_of_tweets)
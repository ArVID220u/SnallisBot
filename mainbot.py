# Import the twython module
from . import twythonaccess
# import time and sys
import time
# import users
from .users import Users
# import fast streamer
from . import FastReplyStreamer
# import apikeys to authenticate streamer
from . import apikeys
# import Thread to be able to run concurrently
from threading import Thread
# randint for the tweet interval
from random import randint
# import setup for all data
from .setup import .



# the main function will be called when this script is called in terminal
# the bash command "python3 mainbot.py" will call this function
def main():

    # set this up with error handling
    while True:
        try:
            setUp()
            break
        except Exception as exception:
            print(exception)
            print("will sleep for 1 hour to avoid exception in setup")
            time.sleep(60*60)
            print("exception sleep in setup now finished; retrying setup")
    
    # create two threads, which will call reply_streamer and tweet_loop
    # use threads to make these threads be able to run concurrently
    reply_streamer_thread = Thread(target = reply_streamer)
    tweet_loop_thread = Thread(target = tweet_loop)
    # start both threads
    reply_streamer_thread.start()
    tweet_loop_thread.start()
    # these threads will run infinitely


def setUp():
    # initialize users
    global users
    # initialize users
    users = Users()
    print("initialized users")
    print("setup complete")





# this function will be executed in one thread, and tweet_loop on the other
# purpose to isolate this in streaming api is to reply to all tweets mentioning self quickly
def reply_streamer():
    print("starting registering for streaming api for fastrelystreamer")
    # initialize the fastreplystreamer
    streamer = FastReplyStreamer(apikeys.CONSUMER_KEY, apikeys.CONSUMER_SECRET, apikeys.ACCESS_TOKEN, apikeys.ACCESS_TOKEN_SECRET) 
    # start the filter
    # nest it in error handling
    while True:
        try:
            streamer.statuses.filter(track=("@" + screen_name))
        except Exception as exception:
            # print the exception and then sleep for an hour
            # the sleep will reset rate limit
            # if twitter's servers were down, they may be up after the sleep
            # after the sleep, the filter function will be called anew
            print(exception)
            print("will sleep for 1 hour to avoid exception in fastreplystreamer")
            time.sleep(60*60)
            print("finished sleep after exception in fastreplystreamer. will now start anew")


# the run loop, which will continue in infinity
def tweet_loop():
    global users
    while True:
        print("start loop")

        
        # the try is for error handling
        # if any of the twython methods (nested or not) raise an exception,
        # then it will be caught in this except clause
        # the except clause will do nothing but sleep for a while,
        # and then continue with the loop
        try:
            user = users.get_user()
            print("will send tweet to user: " + user)
            # send tweet
            while True:
                # generate new tweet
                # first generate a random naumber
                randnum = randint(0,len(kind_tweets)-1)
                tweet = "@" + user + " " + kind_tweets[randnum] + hashtag
                print("tweet generated: " + tweet)
                if len(tweet) < 140 and twythonaccess.send_tweet(tweet):
                    # the generated tweet is okay
                    print("tweet approved or passed")
                    break

            # sleeping point, if need for sleep
            # sleep for one day
            # make the sleep somewhat randomized
            # can range from 5 minutes to 3 days
            # make the distribution curve peak at 24 hours
            # get a random integer between 5 and 2.25*24*60, representing minutes
            # based on calculations, do first loop 5 times and second loop once
            min_sleep = 5
            max_sleep = 2.25*24*60
            sleep_minutes = randint(min_sleep, max_sleep)
            for i in range(0,4):
                # if the value isn't in the specified range, then regenerate the value
                # this will increase the statistical probability of the value falling in the range, while not limiting the value directly
                # first limit the value in a close range, then in a bigger range, order is important
                # this will make the curve like a double-sided stairway with three levels, the middle level being the widest
                if sleep_minutes < 23*60 or sleep_minutes > 27*60:
                    sleep_minutes = randint(min_sleep, max_sleep)
            # second loop, wider, designed to catch almost all values
            for i in range(0,1):
                if sleep_minutes < 6*60 or sleep_minutes > 46*60:
                    sleep_minutes = randint(min_sleep, max_sleep)

            print("will sleep for " + str(sleep_minutes) + " seconds")
            time.sleep(sleep_minutes)
            print("has slept for " + str(sleep_minutes) + " seconds")


        except Exception as exception:
            # print out the exception, and then sleep for 1 hour
            # the exception may be a rate limit, or it may be due to twitter's servers being down
            # either way, a sleep will help
            print(exception)
            print("will sleep for 1 hour to avoid exception")
            time.sleep(60*60)
            print("finished exception sleep; will resume tweet generation loop as normal")




# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()

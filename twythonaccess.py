# This module provides the api twython object, which is used to access the api

# import time, to enable the sleep function
import time
# Import twython
from twython import Twython
# import the api keys
from . import apikeys
# import setup to have the screen_name available
from . import setup
# import threading to schedule reset
from threading import Timer
# import datetime
from datetime import datetime




# store the number of reuests for each application
main_requests_since_last_sleep = 0
mine_requests_since_last_sleep = 0

# neither is sleeping at start
main_is_sleeping = False
mine_is_sleeping = False

# time of last request is used t be able t reset the requests
# utc time is reliable
main_time_of_last_request = datetime.utcnow()
mine_time_of_last_request = datetime.utcnow()


# The api variable is the way to access the api
# there are two authorization possibilities: main or mine application
def authorize(main=True):
    # if more than 16 minutes have elapsed since the last request, the reqests limit can be reset
    check_if_requests_can_be_reset(main)
    if main:
        global main_requests_since_last_sleep
        main_requests_since_last_sleep += 1
        # authorize
        return Twython(apikeys.CONSUMER_KEY, apikeys.CONSUMER_SECRET, apikeys.ACCESS_TOKEN, apikeys.ACCESS_TOKEN_SECRET)
    else:
        global mine_requests_since_last_sleep
        mine_requests_since_last_sleep += 1
        # authorize
        return Twython(apikeys.MINE_CONSUMER_KEY, apikeys.MINE_CONSUMER_SECRET, apikeys.MINE_ACCESS_TOKEN, apikeys.MINE_ACCESS_TOKEN_SECRET)


# this method sends a tweet, by first checking with me
def send_tweet(tweet, in_reply_to_status_id=0):
    # send the tweet first as a dm to arvid220u
    # if he replies with yes, send the tweet.
    # if he replies with no, don't send the tweet (generate a new one)
    # if he replies with pass, don't sendd the tweet and don't generate a new one
    
    # REMOVING CONFIRMATION VIA DM, BECAUSE TWEET GENERATION HAS A HIGH LOWEST QUALITY NOW
    
    # send tweet
    # only main application is allowed to send tweets
    sleep_if_requests_are_maximum(14, main=True)
    # maybe send it in reply to another tweet
    if in_reply_to_status_id == 0:
        # standalone tweet
        authorize(main=True).update_status(status=tweet)
    else:
        # tweet is a reply
        authorize(main=True).update_status(status=tweet, in_reply_to_status_id=in_reply_to_status_id)
    print("sent tweet: " + tweet)

    # RETURN TRUE HERE SO DM WON'T BE SENT. TRUST GSGOTTSNACK.
    return True
    


    # get the most recent dm sent to me. the answer should be newer.
    check_if_requests_are_maximum(13)
    previous_reply_id = authorize().get_direct_messages(include_entities=False)[0]["id"]

    # send the dm to arvid with the tweet
    check_if_requests_are_maximum(13)
    authorize().send_direct_message(screen_name="ArVID220u", text=tweet)
    print("tweet in review: " + tweet)
    arvid_has_approved_or_aborted = False
    while not arvid_has_approved_or_aborted:
        check_if_requests_are_maximum(13)
        # get the dms more recent than the previous reply
        all_dms = authorize().get_direct_messages(include_entities=False, since_id=previous_reply_id)
        response_since_gs_message = ""
        # get the last reply, make sure it's in the right conversation
        # the last reaply is at index 0
        # if all_dms length is greater than 0
        if len(all_dms) > 0:
            last_message_index = 0
            last_message = all_dms[last_message_index]
            last_message_is_arvid = False
            while not last_message_is_arvid:
                if last_message["sender_screen_name"] == "ArVID220u":
                    response_since_gs_message = last_message["text"]
                    last_message_is_arvid = True
                else:
                    last_message_index += 1
                    last_message = all_dms[last_message_index]
            print("last message: " + last_message["text"])
            if last_message_is_arvid:
                print("arvid's reponse: " + response_since_gs_message)
                if response_since_gs_message == "Yes":
                    # send the tweet
                    check_if_requests_are_maximum(13)
                    if in_reply_to_status_id == 0:
                        authorize().update_status(status=tweet)
                    else:
                        authorize().update_status(status=tweet, in_reply_to_status_id=in_reply_to_status_id)
                    print("sent tweet: " + tweet)
                    arvid_has_approved_or_aborted = True
                if response_since_gs_message == "Pass":
                    arvid_has_approved_or_aborted = True
                elif response_since_gs_message == "No":
                    # return false, which will make this function be called again, with a new tweet (hopefully)
                    return False
        if not arvid_has_approved_or_aborted:
            time.sleep(60*6)

    # return true, meaning this function should not be called again
    return True


# This method is called everytime a request is to be made
# IF the requests variable is over limit, then it sleeps for 17 minutes
# if the requests variable isn't over limit, then increment it by one
def sleep_if_requests_are_maximum(limit, main=True):
    if main:
        global main_requests_since_last_sleep
        global main_is_sleeping
        print("Requests since last sleep in main: " + str(main_requests_since_last_sleep))
        if main_requests_since_last_sleep >= limit:
            if not main_is_sleeping:
                main_is_sleeping = True
                # reset after 16 minutes
                Timer(16*60, main_reset_requests).start()
        # if main is sleeping
        if main_is_sleeping:
            print("will sleep")
            time.sleep(16*60)
            print("has slept")
    else:
        global mine_requests_since_last_sleep
        global mine_is_sleeping
        print("Requests since last sleep in mine: " + str(mine_requests_since_last_sleep))
        if mine_requests_since_last_sleep >= limit:
            if not mine_is_sleeping:
                mine_is_sleeping = True
                # reset after 16 minutes
                Timer(16*60, mine_reset_requests).start()
        # if main is sleeping
        if mine_is_sleeping:
            print("will sleep")
            time.sleep(16*60)
            print("has slept")


# if more than 16 minutes have elapsed since the last request, safely reset the count
def check_if_requests_can_be_reset(main=True):
    now_time = datetime.utcnow()
    if main:
        global main_time_of_last_request
        if (now_time - main_time_of_last_request).total_seconds() > 16*60:
            global main_requests_since_last_sleep
            main_requests_since_last_sleep = 0
        main_time_of_last_request = now_time
    else:
        global mine_time_of_last_request
        if (now_time - mine_time_of_last_request).total_seconds() > 16*60:
            global mine_requests_since_last_sleep
            mine_requests_since_last_sleep = 0
        mine_time_of_last_request = now_time


# reset the main requests
def main_reset_requests():
    global main_requests_since_last_sleep
    global main_is_sleeping
    main_requests_since_last_sleep = 0
    main_is_sleeping = False
# reset the mine requests
def mine_reset_requests():
    global mine_requests_since_last_sleep
    global mine_is_sleeping
    mine_requests_since_last_sleep = 0
    mine_is_sleeping = False

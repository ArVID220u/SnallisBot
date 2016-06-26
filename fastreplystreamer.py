# the FastReplyStreamer is a subclass of TwythonStreamer
from twython import TwythonStreamer
# import twythonaccess to be able to send tweets
from . import twythonaccess
# setup needed to access reply_tweet
from . import setup

# the FastReplyStreamer class will use the streaming api to quickly reply to tweets.
# It will be used for filtering all tweets containing the screen name.
# This class could technically be used to reply to all kinds of tweets.
class FastReplyStreamer(TwythonStreamer):
    # don't reply to a particular user more than once
    replied_to_users = set()
    # this function will be called when a tweet is received
    def on_success(self, data):
        # the data variables contains a tweet
        # reply to that tweet
        # generate new tweet
        # first generate a random naumber
        userid = data["user"]["id"]
        # don't reply to a particular user more than once
        if userid in self.replied_to_users:
            return
        self.replied_to_users.add(userid)
        # get its screen name
        twythonaccess.sleep_if_requests_are_maximum(170)
        screenname = twythonaccess.authorize(main=True).show_user(user_id=userid)["screen_name"]
        tweet = "@" + screenname + " " + setup.reply_tweet
        print("will reply to someone with following tweet: " + tweet)
        if twythonaccess.send_tweet(tweet, in_reply_to_status_id=data["id"]):
            # the generated tweet is okay
            print("tweet approved or passed in fastrelystreamer")

    # when an error is caught
    def on_error(self, status_code, data):
        print("STREAMING API ERROR!")
        print("Status code:")
        print(status_code)
        print("Other data:")
        print(data)
        print("END OF ERROR MESSAGE")

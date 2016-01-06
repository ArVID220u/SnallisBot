# import twythonaccess to be able to make twitter requests
from . import twythonaccess
# import apikeys
from . import apikeys
# import twythonstreamer for the SwedishMiner down below
from twython import TwythonStreamer
# import threading
from threading import Thread

# this class provides Swedish usernames
# all unique, and as long as there are users left in Swedish Twitter, this class will keep churning them out
class Users:
    # the added users is a set of the user ids of all that have been added
    added_users = set()
    # the next users is a queue for the users to be returned
    next_users = []
    # the mine followers is also a queue for the users whose follower list hasn't yet been mined
    mine_followers = []

    # initializer
    def __init__(self):
        # create a swedish_miner
        self.swedish_miner = SwedishMiner(apikeys.MINE_CONSUMER_KEY, apikeys.MINE_CONSUMER_SECRET, apikeys.MINE_ACCESS_TOKEN, apikeys.MINE_ACCESS_TOKEN_SECRET)
        # set its users property to self
        # warning: this will create a memory leak, as both references are strong
        self.swedish_miner.users = self
        # start a thread for mining the swedish users
        swedish_miner_thread = Thread(target = self.swedish_miner_streamer)
        swedish_miner_thread.start()


    # start the swedish miner streamer
    def swedish_miner_streamer(self):
        self.swedish_miner.statuses.filter(



# this class finds users based on them sending tweets marked as swedish
class SwedishMiner(TwythonStreamer):
    # this function is called when a tweet is received
    def on_success(self, tweet):
        # add the user
        self.users.add_user(tweet["id"])

    def on_error(self, status_code, data):
        print("STREAMING API ERROR in SwedishStreamer")
        print("Status code:")
        print(status_code)
        print("other data:")
        print(data)
        print("END OF ERROR MESSAGE")

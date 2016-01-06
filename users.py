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


    # add a user to the lists, checking first if it's unique
    def add_user(self, userid):
        if userid in self.added_users:
            # already added this user, abort
            return
        # if there already are too many users in the mine_followers array, disconnect the swedish_miner
        if len(self.mine_followers) > 1000:
            self.swedish_miner.alive = False
            self.swedish_miner.disconnect()
        # add user to added_users
        self.added_users.add(userid)
        # append user to both the minefollowers queue and the nextusers queue
        self.next_users.append(userid)
        self.mine_followers.append(userid)


    # return a screen name of a user
    def get_user(self):
        # if the number of users in next_users is less than 10, mine some followers
        if len(self.next_users) < 10 and len(self.mine_followers) > 0:
            # do it in a separate thread
            mine_followers_thread = Thread(target = self.mine_some_followers)
            mine_followers_thread.start()
        # if next users length is zero, which just should never happen, wait
        while len(self.next_users) == 0:
            time.sleep(6*60)
        # do not respond to protected users
        screenname = ""
        while True:
            # get the frontmost user in the next_users queue
            firstid = self.next_users.pop(0)
            # get the screen name of this particular user
            twythonaccess.sleep_if_requests_are_maximum(170, main=False)
            user = twythonaccess.authorize(main=False).show_user(user_id=userid)
            if not user["protected"]:
                screenname = user["screen_name"]
                break
            elif len(self.next_users) == 0:
                return self.get_user()
        # return it
        return screenname
        


    # mine some followers
    def mine_some_followers(self):
        # if the mine_followers queue contains less than 200 items, start the swedish streamer
        if len(self.mine_followers) < 200 and not self.swedish_miner.alive:
            swedish_miner_thread = Thread(target = self.swedish_miner_streamer)
            swedish_miner_thread.start()
        while len(self.mine_followers) == 0:
            time.sleep(6*60)
        counter = 0
        while True:
            # get the first user
            userid = self.mine_followers.pop(0)
            # get user
            twythonaccess.sleep_if_requests_are_maximum(170, main=False)
            user = twythonaccess.authorize(main=False).show_user(user_id=userid)
            # if user is protected, continue
            if user["protected"]:
                if len(self.mine_followers) == 0:
                    break
                continue
            # get a list of the followers
            twythonaccess.sleep_if_requests_are_maximum(13, main=False)
            followers = twythonaccess.authorize(main=False).get_followers_list(user_id=userid, count=100)["users"]
            for follower in followers:
                if follower["lang"] == "sv":
                    self.add_user(follower["id"])
                    count += 1
            if count > 100 or len(mine_followers) == 0:
                break


    # start the swedish miner streamer
    def swedish_miner_streamer(self):
        # get most of all swedish tweets
        # it performs an or search, with language sv
        self.swedish_miner.alive = True
        self.swedish_miner.statuses.filter(track="i,och,att,det,som,en,på,är,av,för", language="sv")



# this class finds users based on them sending tweets marked as swedish
class SwedishMiner(TwythonStreamer):
    # check if alive
    alive = False
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

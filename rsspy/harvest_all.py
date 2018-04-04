import model.feed as Feed
import config
import time
import sys


print("|+-+ Harvesting @ %s +-+-+-+-+-+-+-+|" % time.strftime("%c"))
feed = Feed.Feed()
feed.harvest_all()



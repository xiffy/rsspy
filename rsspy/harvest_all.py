import model.feed as Feed
import time


print("|+-+ Harvesting @ %s +-+-+-+-+-+-+-+|" % time.strftime("%c"))
feed = Feed.Feed()
feed.harvest_all()

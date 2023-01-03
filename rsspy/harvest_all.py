import rsspy.model.feed as Feed
import time


def main():
    print("|+-+ Harvesting @ %s +-+-+-+-+-+-+-+|" % time.strftime("%c"))
    feed = Feed.Feed()
    feed.harvest_all()


if __name__ == "__main__":
    main()

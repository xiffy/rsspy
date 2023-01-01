import feedparser
#import model.db as dbase
import model.feed as Feed
import config

import sys

#url = 'http://www.thisiscolossal.com/feed/'
#url = 'http://xiffy.nl/rss.xml'
#url = 'https://www.flickr.com/services/feeds/photos_public.gne?id=96811126@N00&format=rss_200'
#url = 'https://www.nrc.nl/rss'
#url = 'https://www.jwz.org/blog/feed/'
url = 'http://www.theregister.co.uk/headlines.atom'

x = feedparser.parse(url)

for e in x.entries:
    print (e.title)
    #contents = ''
    #if hasattr(e, 'content'):
    #    contents = e.content[0].value
    #if hasattr(e, 'summary_detail') and len(e.summary_detail.get('value')) > len(contents):
    #    contents = e.summary_detail.get('value', None)
    #elif len(e.summary) > len(contents):
    #    contents = e.summary
    #print (contents)
#print(x.entries)
#print(x.entries[0].keys())
#for entry in x.entries:
#    print(entry)
#    if hasattr(entry, 'summary_detail'):
#        print(entry.content[0]['value'])
        #print(entry.summary_detail.get('value'))

#feed = Feed.Feed()
#feed.harvest(2)

#feed.description = 'We want our hats back'
#feed.update()
#print (feed.description)
#feed.create(url='https://www.nrc.nl/rss/', description='snelle duiding by het laatste nieuws')
#print (feed.url)


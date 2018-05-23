from . import db as dbase
from . import entry as Entry
import MySQLdb
import feedparser
import time
import copy
import datetime


class Feed():

    def __init__(self, ID=None):
        self.db = dbase.DBase()
        self.entries = []
        self.fields = ['ID', 'url', 'title', 'image', 'description', 'update_interval', 'feed_last_update', 'web_url', 'last_update', 'active']
        if ID:
            self._get(by='ID', value=ID)

    def create(self, url=None, title=None, description=None, image=None, update_interval=59, web_url=None):
        if url:
            if not self._get('url', url):
                try:
                    self.db.cur.execute('insert into feed \
                       (url, title, image, description, update_interval, web_url) \
                       values (%s, %s, %s, %s, %s, %s)' \
                       , (url, title, image, description, \
                          update_interval, web_url))
                    self.db.connection.commit()
                    self.harvest(self.db.cur.lastrowid)
                except MySQLdb.Error as e:
                    self.db.connection.rollback()
                    print(self.db.cur._last_executed)
                    print ("MySQL Error: %s" % str(e))
        return self

    def update(self):
        if self.ID:
            try:
                self.db.cur.execute('update feed \
                      set url = %s, title = %s, image =  %s, description = %s, update_interval = %s, web_url = %s, feed_last_update = %s, active = %s, request_options = %s where ID = %s' \
                      , (self.url, self.title, self.image, self.description, self.update_interval, self.web_url, self.feed_last_update, self.active, self.request_options, self.ID) )
                self.db.connection.commit()
                self.__init__(self.ID)
            except MySQLdb.Error as e:
                self.db.connection.rollback()
                print(self.db.cur._last_executed)
                print ("MySQL Error: %s" % str(e))

    def with_entries(self, amount=10, start=0):
        if not hasattr(self, 'ID'):
            return False
        entry = Entry.Entry()
        entries = entry.fetch_by_feed(self.ID, amount, start)
        for entryID in entries:
            self.entries.append(Entry.Entry(entryID[0]))
        return True

    def harvest(self, ID=None):
        if ID:
            self.__init__(ID)
        self.entries = []

        ts = time.time()
        if self.url:
            print ("%s : %s" % (self.title,self.url))
            response = feedparser.parse(self.url, agent="Feedfetcher (https://rss.xiffy.nl/fetcher.php)")
            if not hasattr(response, 'status'):
                print("Timeout")
            else:
                print (response.status)
                if response.status in [200, 301, 302, 307]:
                    self._parse_feed(response.feed)
                    for _entry in response.entries:
                        entry = Entry.Entry()
                        entry.parse_and_create(_entry, self.ID)
                        self.feed_last_update = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    if response.status in [301, 302, 307]:
                        self.url = response.get('href', self.url)
                elif response.status in [410, 404]:
                    self.active = 0
        self.last_update = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        self.update()

    def harvest_all(self):
        feeds = self._get_all(harvest=True)
        if feeds:
            [self.harvest(feed[0]) for feed in feeds]

    def get_all(self, exclude_ids=[]):
        return self._get_all(exclude_ids=exclude_ids)

    def get_recents(self, amount=10, start=0):
        """
        get recent entries of any feed
        :param amount: (int) amount to fetch, defaults to 10
        :param start: (int) start, defaults to 0
        """
        #self.db.cur.execute('select feed.ID, feed.title, feed.description, feed.web_url, entry.ID, entry.title, entry.contents, entry.published from entry left join feed on feed.ID = entry.feedID order by published desc limit 0, 10')
        self.db.cur.execute('select feed.ID, entry.ID from entry left join feed on feed.ID = entry.feedID order by published desc limit %s, %s', (int(start), int(amount,),))

        return self.db.cur.fetchall()

    def get_by_bookmarks(self, bookmarks):
        """
        expects a list of bookmarkrecords gets the feed and entries based on these
        """
        entries = [row[2] for row in bookmarks]
        if len(entries) is 0:
            return False
        fs = ','.join(['%s'] * len(entries))
        try:
            self.db.cur.execute('select feed.ID, entry.ID, created_at from bookmark left join entry on bookmark.entryID = entry.ID left join feed on feed.ID = entry.feedID where entry.ID in (%s) order by bookmark.created_at desc' % fs,tuple(entries) )
            return self.db.cur.fetchall()
        except MySQLdb.Error as e:
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))

    def _get(self, by=None, value=None):
        """
        get one feed by given method and value
        :param by: field to use in where
        :param value: value to be used for retrieval
        """
        if 'ID' in by:
            self.db.cur.execute('select * from feed where ID = %d' % value)
        if 'url' in by:
            self.db.cur.execute('select * from feed where url = %s', (value,))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.url, self.title, self.image, \
            self.description, self.update_interval, \
            self.feed_last_update, self.web_url, \
            self.last_update, self.active, self.request_options = row
        else:
            return False
        return True

    def _get_all(self, harvest=False, active=True, exclude_ids=[]):
        """
        get all the active feeds
        :param harvest: Bool, if True only harvestable feeds are included
        :param active: Bool, defaults True, show only active feeds
        """
        q = 'select ID from feed where active = %s' % active
        if harvest:
            q += ' and date_add(feed_last_update, interval update_interval minute) < now() '
        try:
            self.db.cur.execute(q)
        except MySQLdb.Error as e:
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))
            return False

        return self.db.cur.fetchall()

    def _parse_feed(self, feed):
        self.title = feed.title if hasattr(feed, 'title') else None
        self.description = feed.sub_title if hasattr(feed, 'sub_title') else None
        self.image = feed.image.get('href', None) if hasattr(feed, 'image') else None

        for link in feed.links:
            if link.get('type', None) == 'text/html':
                self.web_url = link.href
        return True

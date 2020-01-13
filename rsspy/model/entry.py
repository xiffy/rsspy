from . import db as dbase
from . import user as User
from . import bookmark as Bookmark
from . import feed as Feed
import MySQLdb
from flask import session
import time
import datetime
import re


class Entry:

    def __init__(self, ID=None, title=None, description=None, contents=None, url=None, guid=None, \
                       last_update=None, entry_created=None, published=None, feedID=None):
        self.db = dbase.DBase()
        self.ID = ID
        self.title = title
        self.description = description
        self.contents = contents
        self.url = url
        self.guid = guid
        self.last_update = last_update
        self.entry_created = entry_created
        self.published = published
        self.feedID = feedID
        if self.ID:
            self._get(by='ID', value=ID)

    def parse_and_create(self, entry, feedID):
        """ digest python_feedparser entries and creates rsspy entries """
        if not hasattr(entry, 'link'):
            return False

        contents = ''
        if hasattr(entry, 'content'):
            contents = entry.content[0].value
        if hasattr(entry, 'summary_detail') and len(entry.summary_detail.get('value')) > len(contents):
            contents = entry.summary_detail.get('value', None)
        elif len(entry.summary) > len(contents):
            contents = entry.summary
        if hasattr(entry, 'published_parsed' ):
            published = datetime.datetime(*(entry.published_parsed[0:6])).strftime('%Y-%m-%d %H:%M:%S')
        else:
            published = time.strftime('%Y-%m-%d %H:%M:%S')
        # add an image
        if hasattr(entry, 'links'):
            for r in entry.links:
                if (r.get('rel', None) == 'enclosure'
                   and 'image' in r.get('type', None)
                   and r.get('href') not in contents):
                    contents = contents + ' <br/><img src="%s">' % r.get('href', "#")
        return self.create(feedID=feedID, title=entry.title, description=entry.summary, contents=contents,
                           url=entry.link, guid=entry.link,published=published)

    def create(self, feedID=None, title=None, description=None, contents=None, url=None, guid=None, published=None):
        if feedID and url and (title or description):
            self.feedID = feedID
            if not self._get('feedID_url', [self.feedID, url]):
                try:
                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    contents = self.filter_unwanted(contents)
                    self.db.cur.execute('insert into entry \
                       (feedID, title, description, contents, url, guid, entry_created, published)  values (%s, %s, %s, %s, %s, %s, %s, %s)' ,
                        (feedID, title[:255], description, contents, url, guid, timestamp, published))
                    self.db.connection.commit()
                    self.__init__(self.db.cur.lastrowid)
                    return True
                except MySQLdb.Error as e:
                    self.db.connection.rollback()
                    print(self.db.cur._last_executed)
                    print ("MySQL Error: %s" % str(e))

    def fetch_by_feed(self, feedID=None, amount=10, start=0, **kwargs):
        try:
            self.db.cur.execute('select ID from entry where feedID = %s order by published desc limit %s, %s ' %
                            (int(feedID), int(start), int(amount)))
            return self.db.cur.fetchall()
        except MySQLdb.Error as e:
            self.db.connection.rollback()
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))

    def search(self, q, amount=10, start=0):
        try:
            self.db.cur.execute('select feedID, ID, title, match(title, description, contents) against ("%s") as score from entry where match(title, description, contents) against ("%s") order by score desc limit %s, %s' % (q, q, int(start), int(amount)))
            return self.db.cur.fetchall()
        except MySQLdb.Error as e:
            self.db.connection.rollback()
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))

    def searchamount(self, q):
        try:
            self.db.cur.execute('select count(*) as results from entry where match(title, description, contents) against ("%s")' % q)
            row = self.db.cur.fetchone()
            return row[0]
        except MySQLdb.Error as e:
            self.db.connection.rollback()
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))

    @property
    def bookmarked(self):
        user = User.User()
        if user.verify(session.get('das_hash', None)):
            b = Bookmark.Bookmark()
            return b.bookmarked(userID=user.ID, entryID=self.ID)

    def _get(self, by=None, value=None):
        if 'ID' == by:
            self.db.cur.execute('select * from entry where ID = %d' % value)
        elif 'feedID_url' in by:
            self.db.cur.execute('select * from entry where feedID = %s and url = "%s"' % (value[0], value[1][:255]))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.feedID, self.title, self.description, \
            self.contents, self.url, self.guid, self.last_update, \
            self.entry_created, self.published = row
        else:
            return False
        return True

    def filter_unwanted(self, contents):
        content_filter = Feed.Feed(self.feedID).content_filter
        if content_filter:
            print(content_filter)
            if content_filter == 'nl2br':
                contents = contents.replace('\n', '<br>\n')
        # remove slashdot comments iframe, laden with javascript and css
        contents = re.sub('(?:<iframe.*slashdot.org*.[^>]*)(?:(?:\/>)|(?:>.*?<\/iframe>))', '', contents)

        return contents
from . import db as dbase
import MySQLdb
import time
import datetime

class Entry():

    def __init__(self, ID=None):
        self.db = dbase.DBase()
        self.fields = ['ID', 'feedID', 'title', 'description', 'contents', 'url', 'guid', 'last_update', 'entry_created']
        if ID:
            self._get(by='ID', value=ID)

    def create(self, feedID=None, title=None, description=None, contents=None, url=None, guid=None):
        if feedID and url and (title or description):
            if not self._get('feedID_url', [feedID, url]):
                try:
                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    self.db.cur.execute('insert into entry \
                       (feedID, title, description, contents, url, guid, item_created) \
                       values (%s, %s, %s, %s, %s, %s, %s)' \
                       , (feedID, title[:255], description, contents, url, guid, timestamp))
                    self.db.connection.commit()
                    self.__init__(self.db.cur.lastrowid)
                except MySQLdb.Error as e:
                    self.db.connection.rollback()
                    print(self.db.cur._last_executed)
                    print ("MySQL Error: %s" % str(e))

    def fetch_by_feed(self, feedID=None, amount=10, start=0, **kwargs):
        try:
            self.db.cur.execute('select ID from entry where feedID = %s limit %s, %s',
                            (int(feedID), int(start), int(amount)))
            return  self.db.cur.fetchall()
        except MySQLdb.Error as e:
            self.db.connection.rollback()
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))

    def _get(self, by=None, value=None):
        if 'ID' == by:
            self.db.cur.execute('select * from entry where ID = %d' % value)
        elif 'feedID_url' in by:
            self.db.cur.execute('select * from entry where feedID = %s and url = %s', (value[0], value[1][:255]))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.feedID, self.title, self.description, \
            self.contents, self.url, self.guid, self.last_update, \
            self.entry_created = row
        else:
            return False
        return True



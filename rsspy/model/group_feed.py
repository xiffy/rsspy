from . import db as dbase
from . import feed as Feed
import MySQLdb
from flask import request
import time
import datetime

class GroupFeed():

    def __init__(self, ID=None, groupID=None, feedID=None):
        self.db = dbase.DBase()
        self.ID = ID
        self.groupID = groupID
        self.feedID = feedID
        if groupID and feedID and not ID:
            self._create(groupID=groupID, feedID=feedID)
        if ID:
            self._get(by='ID', value=ID)


    def get_feeds(self, groupID=None):
        """
        return all feeds from a group
        """
        if not groupID:
            return False
        feeds = []
        feedIDs = self._all_from_group(groupID=groupID)
        for ID in feedIDs:
            feeds.append(Feed.Feed(ID=ID))
        return feeds

    def _all_from_group(self, groupID=None):
        """
        return all the groupID's of a user as a list
        :param userID: the user of whom we fetch the groupIDs
        """
        if not groupID:
            return []
        try:
            self.db.cur.execute('select feedID from `group_feed` where groupID = %s',
                            (int(groupID), ))
            return  self.db.cur.fetchall()
        except MySQLdb.Error as e:
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))
            return []

    def delete(self, groupID=None, feedID=None):
        if groupID and feedID:
            self.db.cur.execute('delete from group_feed where groupID = %s and feedID = %s ' % (groupID, feedID))
            self.db.connection.commit()

    def _get(self, by='ID', value=None):
        if not value:
            return False
        self.db.cur.execute('select * from `group_feed` where ID = %d' % value)

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.groupID, self.feedID = row
        else:
            print(self.db.cur._last_executed)
            return False
        return True

    def _create(self, feedID=None, groupID=None):
        if not feedID or not groupID:
            return false
        try:
            self.db.cur.execute('insert into group_feed (feedID, groupID) values (%s, %s)' % (feedID, groupID))
            self.db.connection.commit()
            self.__init__(self.db.cur.lastrowid)
        except MySQLdb.Error as e:
            print(self.db.cur._last_executed)
            self.db.connection.rollback()
            print ("MySQL Error: %s" % str(e))
            return []



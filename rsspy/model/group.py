from . import db as dbase
from . import group_feed as GroupFeed
import MySQLdb
from flask import request
import time
import datetime

class Group():

    def __init__(self, ID=None, description=None, userID=None, aggregation=None, frequency=None, last_sent=None):
        self.db = dbase.DBase()
        self.userID = userID
        self.description = description
        self.aggregation = aggregation
        self.frequency = frequency
        self.last_sent = last_sent
        if ID:
            self._get(by='ID', value=ID)

    def get_groups(self, userID=None, level=2):
        """
        return all groups with feeds included
        """
        if not userID:
            return False
        groups = []
        groupIDs = self._all_from_user(userID=userID)
        for ID in groupIDs:
            groups.append(Group(ID=ID))
            group_feed = GroupFeed.GroupFeed()
            feeds = group_feed.get_feeds(groupID=ID[0])
            groups[-1].feeds = feeds
        return groups


    def _all_from_user(self, userID=None):
        """
        return all the groupID's of a user as a list
        :param userID: the user of whom we fetch the groupIDs
        """
        if not userID:
            return []
        try:
            self.db.cur.execute('select ID from `group` where userID = %s',
                            (int(userID), ))
            return  self.db.cur.fetchall()
        except MySQLdb.Error as e:
            self.db.connection.rollback()
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))
            return []


    def _get(self, by='ID', value=None):
        """
        get one group by given method and value
        :param by: field to use in where
        :param value: value to be used for retrieval
        """
        if not value:
            return False
        if 'ID' in by:
            self.db.cur.execute('select * from `group` where ID = %d' % value)
        if 'description' in by:
            self.db.cur.execute("select * from `group` where description = %s", (value,))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.description, self.userID, self.aggregation, \
            self.frequency, self.last_sent = row
        else:
            print(self.db.cur._last_executed)
            return False
        return True



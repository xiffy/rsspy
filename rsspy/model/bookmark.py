from . import db as dbase
import MySQLdb
from flask import request
import time
import datetime

class Bookmark():

    def __init__(self, ID=None, userID=None, entryID=None):
        self.db = dbase.DBase()
        self.ID = ID
        self.userID = userID
        self.entryID = entryID
        if ID:
            self._get(by='ID', value=ID)

    def get_bookmarks(self, userID=None):
        """
        return all bookmarks from a user
        """
        if not userID:
            return False
        return self._all_from_user(userID=userID)

    @classmethod
    def add(cls, userID=None, entryID=None):
        db = dbase.DBase()
        if not userID or not entryID:
            return False
        try:
            db.cur.execute("insert into bookmark (userID, entryID) values(%s, %s)", (int(userID), int(entryID),))
            db.connection.commit()
            return {'bookmarkid': db.cur.lastrowid}
        except MySQLdb.Error as e:
            db.connection.rollback()
            print(db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))

    def delete(self):
        try:
            self.db.cur.execute("delete from bookmark where ID=%s", (int(self.ID),))
            self.db.connection.commit()
        except MySQLdb.Error as e:
            self.db.connection.rollback()
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))

    def _all_from_user(self, userID=None):
        """
        return all the groupID's of a user as a list
        :param userID: the user of whom we fetch the groupIDs
        """
        if not userID:
            return []
        try:
            self.db.cur.execute('select * from `bookmark` where userID = %s',
                            (int(userID), ))
            return self.db.cur.fetchall()
        except MySQLdb.Error as e:
            self.db.connection.rollback()
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))
            return []


    def _get(self, by='ID', value=None):
        if not value:
            return False
        self.db.cur.execute('select * from `bookmark` where ID = %d' % value)

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.userID, self.entryID, self.created_at = row
        else:
            print(self.db.cur._last_executed)
            return False
        return True

    def bookmarked(self, userID=None, entryID=None):
        if not userID or not entryID:
            return False
        try:
            self.db.cur.execute('select * from bookmark where userID=%s and entryID=%s', (userID, entryID,))
            return self.db.cur.fetchone()
        except MySQLdb.Error as e:
            print(self.db.cur._last_executed)
            print ("MySQL Error: %s" % str(e))
            return False




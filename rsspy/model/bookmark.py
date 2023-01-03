import sqlite3
from .db import DBase


class Bookmark:
    def __init__(self, ID=None, userID=None, entryID=None):
        self.db = DBase()
        self.ID = ID
        self.userID = userID
        self.entryID = entryID
        if ID:
            self._get(by="ID", value=ID)

    def get_bookmarks(self, userID=None, amount=10, start=0):
        """
        return all bookmarks from a user
        """
        if not userID:
            return False
        return self._all_from_user(userID=userID, amount=amount, start=start)

    @classmethod
    def add(cls, userID=None, entryID=None):
        db = DBase()
        if not userID or not entryID:
            return False
        try:
            db.cur.execute(
                "insert into bookmark (userID, entryID) values(?, ?)",
                (int(userID), int(entryID)),
            )
            db.connection.commit()
            return {"bookmarkid": db.cur.lastrowid}
        except sqlite3.Error as e:
            db.connection.rollback()
            print("MySQL Error: %s" % str(e))

    def delete(self):
        try:
            self.db.cur.execute("delete from bookmark where ID=?", (int(self.ID),))
            self.db.connection.commit()
        except sqlite3.Error as e:
            self.db.connection.rollback()
            print("sqlite Error: %s" % str(e))

    def _all_from_user(self, userID=None, amount=10, start=0):
        """
        return all the groupID's of a user as a list
        :param userID: the user of whom we fetch the groupIDs
        """
        if not userID:
            return []
        try:
            self.db.cur.execute(
                "select * from `bookmark` where userID = ? order by created_at desc limit ?, ?",
                (int(userID), int(start), int(amount)),
            )
            return self.db.cur.fetchall()
        except sqlite3.Error as e:
            self.db.connection.rollback()
            print("sqlite Error: %s" % str(e))
            return []

    def _get(self, by="ID", value=None):
        if not value:
            return False
        self.db.cur.execute("select * from `bookmark` where ID = ?", (value,))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.userID, self.entryID, self.created_at = row
        else:
            return False
        return True

    def bookmarked(self, userID=None, entryID=None):
        if not userID or not entryID:
            return False
        try:
            self.db.cur.execute(
                "select * from bookmark where userID=? and entryID=?", (userID, entryID)
            )
            return self.db.cur.fetchone()
        except sqlite3.Error as e:
            print("sqlite Error: %s" % str(e))
            return False

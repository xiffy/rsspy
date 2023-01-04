from . import db as dbase
from .group_feed import GroupFeed
import sqlite3


class Group:
    def __init__(
        self,
        ID=None,
        description=None,
        userID=None,
        aggregation=None,
        frequency=None,
        last_sent=None,
        issue=None,
    ):
        self.db = dbase.DBase()
        self.ID = ID
        self.userID = userID
        self.description = description
        self.aggregation = aggregation
        self.frequency = frequency
        self.last_sent = last_sent
        self.issue = issue
        if self.ID:
            self._get(by="ID", value=ID)
        elif self.description and self.userID:
            self._create()

    @property
    def feeds(self):
        groupfeed = GroupFeed()
        if self.ID:
            return groupfeed.get_feeds(self.ID)
        else:
            return []

    def get_groups(self, userID=None, level=2):
        """
        return all groups with feeds included
        """
        if not userID:
            return False
        groups = []
        groupIDs = self._all_from_user(userID=userID)
        for ID in groupIDs:
            groups.append(Group(ID=ID[0]))
        return groups

    def get_recents(self, amount=10, start=0):
        if self.ID:
            try:
                self.db.cur.execute(
                    "select feed.ID, entry.ID from `group` "
                    "left join group_feed on group_feed.groupID = `group`.ID "
                    "left join feed on `group_feed`.feedID = feed.ID "
                    "left join entry on feed.ID = entry.feedID "
                    "where `group`.ID = ? "
                    "order by published desc "
                    "limit ?, ?",
                    (self.ID, start, amount),
                )
                return self.db.cur.fetchall()
            except sqlite3.Error as e:
                print("sqlite Error: %s" % str(e))
                return []

    def update_sent(self):
        if self.ID:
            try:
                self.db.cur.execute(
                    "update `group` set last_sent = CURRENT_TIMESTAMP, issue = issue + 1 where ID = ?",
                    (self.ID,),
                )
                self.db.connection.commit()
            except sqlite3.Error as e:
                print("update_sent():")
                print("sqlite Error: %s" % str(e))
                return []

    def delete(self):
        if self.ID:
            try:
                self.db.cur.execute("delete from `group` where ID = ?", (self.ID,))
                self.db.connection.commit()
                return True
            except sqlite3.Error as e:
                self.db.connection.rollback()
                print("sqlite Error: %s" % str(e))
                return False

    def get_digestables(self):
        self.db.cur.execute("select id from `group` where aggregation = ?", ("email",))
        return self.db.cur.fetchall()

    def get_digestable(self):
        if self.ID:
            try:

                self.db.cur.execute(
                    "select feed.ID, entry.ID from `group` "
                    "left join group_feed on group_feed.groupID = `group`.ID "
                    "left join feed on `group_feed`.feedID = feed.ID "
                    "left join entry on feed.ID = entry.feedID "
                    "where `group`.ID = ? "
                    f"and `group`.last_sent < datetime('now', 'localtime', '- {self.frequency} hour') "
                    "and entry.entry_created > ? order by published desc",
                    (self.ID, self.last_sent),
                )
                return self.db.cur.fetchall()
            except sqlite3.Error as e:
                print("digest")
                print("sqlite Error: %s" % str(e))
                return []

    def _all_from_user(self, userID=None):
        """
        return all the groupID's of a user as a list
        :param userID: the user of whom we fetch the groupIDs
        """
        if not userID:
            return []
        try:
            self.db.cur.execute(
                "select ID from `group` where userID = ?", (int(userID),)
            )
            return self.db.cur.fetchall()
        except sqlite3.Error as e:
            print("MySQL Error: %s" % str(e))
            return []

    def _get(self, by="ID", value=None):
        """
        get one group by given method and value
        :param by: field to use in where
        :param value: value to be used for retrieval
        """
        if not value:
            return False
        if "ID" in by:
            self.db.cur.execute("select * from `group` where ID = ?", (value,))
        if "description" in by:
            self.db.cur.execute("select * from `group` where description = ?", (value,))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.description, self.userID, self.aggregation, self.frequency, self.last_sent, self.issue = (
                row
            )
        else:
            print("_get: now rows found")
            return False
        return True

    def _create(self):
        try:
            self.db.cur.execute(
                "insert into `group` (description, userID, aggregation, frequency) values (?, ?, ?, ?)",
                (self.description, self.userID, self.aggregation, self.frequency),
            )
            self.db.connection.commit()
            self.ID = self.db.cur.lastrowid
        except sqlite3.Error as e:
            print("sqlite Error: %s" % str(e))
            self.db.connection.rollback()
            return []

import argon2.exceptions

from .db import DBase
from .bookmark import Bookmark
from flask import request, session
from argon2 import PasswordHasher
import uuid


class UserDevice:
    def __init__(self, ID=None, userID=None, ip=None, agent=None, das_hash=None):
        self.db = DBase()
        self.userID = userID
        self.ip = ip
        self.agent = agent
        self.das_hash = das_hash
        self.fields = ["ID", "userID", "ip", "agent", "das_hash", "lastVisit"]
        if ID:
            self._get(by="ID", value=ID)
        elif userID:
            self._get(by="userID", value=userID)
        elif das_hash:
            self._get(by="das_hash", value=das_hash)

    def verify(self, das_hash=None):
        self._get("das_hash", das_hash)
        if not self.userID:
            return False
        session["das_hash"] = self.das_hash
        return True

    def _get(self, by="ID", value=None):
        """
        get one user by given method and value
        :param by: field to use in where
        :param value: value to be used for retrieval
        """
        if not value:
            return False
        if "ID" in by:
            self.db.cur.execute("select * from user_device where ID = ?", (value,))
        if "userID" in by:
            self.db.cur.execute("select * from user_device where userID = ?", (value,))
        if "das_hash" in by:
            self.db.cur.execute("select * from user where das_hash = ?", (value,))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.userID, self.ip, self.agent, self.das_hash, self.lastVisit = (
                row
            )
            if not self.das_hash:
                self._update_hash()
        else:
            print(f"No user_device found: {by} - {value}")
            return False
        return True

    def _update_hash(self):
        if self.userID:
            self.das_hash = str(uuid.uuid1())
            self.db.cur.execute(
                "update user_device set das_hash = ? where userID = ?",
                (self.das_hash, self.userID),
            )
            self.db.connection.commit()


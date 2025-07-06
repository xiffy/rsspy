import json

from .db import DBase
from flask import request, session
import uuid


class UserDevice:
    def __init__(self, ID=None, userID=None, ip=None, agent=None, das_hash=None):
        self.db = DBase()
        self.userID = userID
        self.ip = ip
        self.agent = agent
        self.das_hash = das_hash
        self.lastvisit = None
        self.fields = ["ID", "userID", "ip", "agent", "das_hash", "lastvisit"]

    def verify(self):
        self.db.cur.execute("select ID, userID, ip, agent, das_hash, lastvisit from user_device where userID=? and das_hash = ?", (self.userID, self.das_hash))
        row = self.db.cur.fetchone()
        if row is not None:
            session["das_hash"] = self.das_hash
            return True
        elif self.das_hash:
            self.db.cur.execute("insert into user_device (userID, ip, agent, das_hash) "
                                "values (?, ?, ?, ?)",
                                (self.userID, request.remote_addr, str(request.user_agent) ,self.das_hash))
            self.db.connection.commit()
            session["das_hash"] = self.das_hash
            return True
        return False


    def get_by_hash(self):
        if not self.das_hash:
            return None
        self.db.cur.execute("select * from user_device where das_hash = ?", (self.das_hash,))
        row = self.db.cur.fetchone()
        if row:
            self.ID, self.userID, self.ip, self.agent, self.das_hash, self.lastvisit = (
                row
            )
        else:
            self.userID = None
        return self


    def find_session(self, client_info=None):
        if not self.userID:
            return None
        if client_info:
            client_info = json.loads(client_info)
        self.db.cur.execute("select * from user_device where userID = ?", (self.userID,))
        client_info["userAgent"] = str(request.user_agent)
        client_info = json.dumps(client_info)
        rows = self.db.cur.fetchall()
        if rows:  # currently llosly based on user-agent
            for row in rows:
                if row[3] == client_info:
                    return row[4]
        # a new client
        self.das_hash = str(uuid.uuid1())
        self.db.cur.execute("insert into user_device (userID, ip, agent, das_hash) "
                             "values (?, ?, ?, ?)",
                             (self.userID, request.remote_addr, client_info ,self.das_hash))
        self.db.connection.commit()
        return self.das_hash


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
            self.ID, self.userID, self.ip, self.agent, self.das_hash, self.lastvisit = (
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


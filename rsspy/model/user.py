import argon2.exceptions

from .db import DBase
from .bookmark import Bookmark
from flask import request, session
from argon2 import PasswordHasher
import uuid

from .user_device import UserDevice


class User:
    def __init__(self, ID=None, username=None, email=None, das_hash=None):
        self.db = DBase()
        self.username = username
        self.email = email
        self.current_hash = das_hash
        self.fields = ["ID", "username", "password", "lastvisit", "das_hash", "email"]
        if ID:
            self._get(by="ID", value=ID)
        elif username:
            self._get(by="username", value=username)

    def do_login(self):
        if self._get("username", request.form["username"]):
            try:
                self._verify_password(request.form["password"])
                return True
            except argon2.exceptions.VerifyMismatchError:
                pass
            except argon2.exceptions.VerificationError:
                pass
            self._destroy()
            return False

        return False

    def verify(self, das_hash=None):
        user_device = UserDevice(das_hash=das_hash)
        user_device.get_by_hash()
        if user_device.userID:
            self._get(by="ID", value=user_device.userID)
            session["das_hash"] = user_device.das_hash
            return True
        return False

    @property
    def bookmarks(self):
        if not self.ID:
            return None
        b = Bookmark()
        return b.get_bookmarks(userID=self.ID)

    def _get(self, by="ID", value=None):
        """
        get one user by given method and value
        :param by: field to use in where
        :param value: value to be used for retrieval
        """
        if not value:
            return False
        if "ID" in by:
            self.db.cur.execute("select * from user where ID = ?", (value,))
        if "username" in by:
            self.db.cur.execute("select * from user where username = ?", (value,))
        if "das_hash" in by:
            self.db.cur.execute("select * from user where das_hash = ?", (value,))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.username, self.password, self.lastvisit, self.current_hash, self.email = (
                row
            )
            self._update_hash()
        else:
            print(f"No user found: {by} - {value}")
            return False
        return True

    def _update_hash(self):
        if self.username:
            user_device = UserDevice(userID=self.ID, das_hash=self.current_hash)
            if self.current_hash:
                user_device.verify()

            #  self.current_hash = str(uuid.uuid1())
            #  self.db.cur.execute(
            #     "update user set das_hash = ? where username = ?",
            #     (self.current_hash, self.username),
            #  )
            #  self.db.connection.commit()

    def _verify_password(self, passwd):
        ph = PasswordHasher()
        # print(ph.verify(self.password, passwd))
        return ph.verify(self.password, passwd)

    def _destroy(self):
        self.ID = None
        self.username = None
        self.password = None
        self.current_hash = None

    @staticmethod
    def _hash_it_real_good(passwd):
        ph = PasswordHasher()
        return ph.hash(passwd)

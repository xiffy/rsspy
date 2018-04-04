from . import db as dbase
import MySQLdb
from flask import request
from argon2 import PasswordHasher
from argon2 import exceptions as argon_except
import uuid
import time
import datetime

class User():

    def __init__(self, ID=None, username=None, email=None, das_hash=None):
        self.db = dbase.DBase()
        self.username = username
        self.email = email
        self.das_hash = das_hash
        self.fields = ['ID', 'username', 'password', 'lastvisit', 'das_hash', 'email']
        if ID:
            self._get(by='ID', value=ID)

    def do_login(self):
        if self._get('username', request.form['username']):
            try:
                self._verify_password(request.form['password'])
            except argon_except.VerifyMismatchError:
                self._destroy()
                return False
            return True
        return False

    def verify(self, das_hash=None):
        self._get('das_hash', das_hash)
        if not self.username:
            return False
        return True

    def _get(self, by='ID', value=None):
        """
        get one user by given method and value
        :param by: field to use in where
        :param value: value to be used for retrieval
        """
        if not value:
            return False
        if 'ID' in by:
            self.db.cur.execute('select * from user where ID = %d' % value)
        if 'username' in by:
            self.db.cur.execute("select * from user where username = %s", (value,))
        if 'das_hash' in by:
            self.db.cur.execute("select * from user where das_hash = %s", (value,))

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.username, self.password, self.lastvisit, \
            self.das_hash, self.email = row
            if not self.das_hash:
                self._update_hash()
        else:
            print(self.db.cur._last_executed)
            return False
        return True

    def _update_hash(self):
        if self.username:
            self.das_hash = str(uuid.uuid1())
            self.db.cur.execute('update user set das_hash = %s where username = %s', (self.das_hash,self.username,))
            self.db.connection.commit()

    def _verify_password(self, passwd):
        ph = PasswordHasher()
        return ph.verify(self.password, passwd)

    def _destroy(self):
        self.ID = None
        self.username = None
        self.password = None
        self.das_hash = None

    @staticmethod
    def _hash_it_real_good(passwd):
        ph = PasswordHasher()
        return  ph.hash(passwd)




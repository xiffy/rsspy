import MySQLdb
import sys
sys.path.append('../')
import config


class DBase:

    def __init__(self):
        self.connection = MySQLdb.connect(**config.MYSQLDB)
        self.cur = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

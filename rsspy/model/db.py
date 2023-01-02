import sqlite3
from rsspy.config import Config


class DBase:
    def __init__(self):
        self.connection = sqlite3.connect(Config.SQLITE.value)
        self.cur = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

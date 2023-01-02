import sqlite3
from os.path import join
from rsspy.config import Config


class DBase:
    def __init__(self):
        self.connection = sqlite3.connect(
            join(Config.PROJECT_ROOT.value, Config.SQLITE.value)
        )
        self.cur = self.connection.cursor()
        self.connection.set_trace_callback(print)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

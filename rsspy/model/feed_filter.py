from . import db as dbase


class FeedFilter:
    def __init__(self, ID=None, feedID=None, content_filter=None):
        self.db = dbase.DBase()
        self.ID = ID
        self.feedID = feedID
        self.content_filter = content_filter
        if feedID or ID:
            self._get(ID=ID, feedID=feedID)

    def _get(self, ID=None, feedID=None):
        if ID:
            self.db.cur.execute("select * from `feed_filter` where ID = ?", (ID,))
        elif feedID:
            self.db.cur.execute(
                "select * from `feed_filter` where feedID = ?", (feedID,)
            )
        row = self.db.cur.fetchone()
        if row:
            self.ID, self.feedID, self.content_filter = row

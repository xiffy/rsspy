import sqlite3
import ssl

import requests
import feedparser
import time
import datetime

from .db import DBase
from .entry import Entry
from .feed_filter import FeedFilter


class Feed:
    def __init__(
        self,
        ID=None,
        url=None,
        title=None,
        image=None,
        description=None,
        update_interval=None,
        web_url=None,
        feed_last_update=None,
        active=None,
        last_update=None,
        request_options=None,
    ):
        self.db = DBase()
        self.ID = int(ID) if ID else None
        self.url = url
        self.title = title
        self.image = image
        self.description = description
        self.update_interval = update_interval
        self.web_url = web_url
        self.feed_last_update = feed_last_update
        self.active = active
        self.last_update = last_update
        self.request_options = request_options
        # must become a property -and generator-
        self.entries = []
        if ID:
            self._get(by="ID", value=ID)

    @property
    def content_filter(self):
        if self.ID:
            return FeedFilter(feedID=self.ID).content_filter
        else:
            return None

    def create(
        self,
        url=None,
        title=None,
        description=None,
        image=None,
        update_interval=59,
        web_url=None,
    ):
        if url:
            if not self._get(by="url", value=url):
                cursor = self.db.connection.cursor()
                try:
                    cursor.execute(
                        "insert into feed (url, update_interval) values (?, ?)",
                        (url, update_interval),
                    )
                    self.db.connection.commit()
                    cursor.close()
                    self.harvest(self.db.cur.lastrowid)
                except sqlite3.Error as e:
                    self.db.connection.rollback()
                    print("sqlite Error: %s" % str(e))
            else:
                print(f"bestaat al?")
        return self

    def update(self):
        if self.ID:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "update feed "
                    "set url = ?, title = ?, image = ?, description = ?, update_interval = ?, web_url = ?, "
                    "feed_last_update = ?, active = ?, last_update = ?, request_options = ? "
                    "where ID = ?",
                    (
                        self.url,
                        self.title,
                        self.image,
                        self.description,
                        self.update_interval,
                        self.web_url,
                        self.feed_last_update,
                        self.active,
                        self.last_update,
                        self.request_options,
                        self.ID,
                    ),
                )
                self.db.connection.commit()
                cursor.close()
                self.__init__(self.ID)
            except sqlite3.Error as e:
                self.db.connection.rollback()
                print("feed.update() - sqlite error: %s" % str(e))

    def with_entries(self, amount=10, start=0):
        if not hasattr(self, "ID"):
            return False
        entry = Entry()
        self.entries = [
            Entry(entryID[0]) for entryID in entry.fetch_by_feed(self.ID, amount, start)
        ]
        return True

    def harvest(self, ID=None):
        if ID:
            self.__init__(ID)
        self.entries = []

        ts = time.time()
        if self.url:
            print("%s : %s" % (self.title, self.url))
            request_headers = {}
            if self.request_options:
                request_headers["Cookie"] = self.request_options
            headers = {
                "user-agent": "rsspy harvester 0.9 (https://github.com/xiffy/rsspy)"
            }
            try:
                response = requests.get(self.url, headers=headers)
            except requests.exceptions.SSLError:
                self.last_update = datetime.datetime.fromtimestamp(ts).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                self.update()
                print(f"SSL Error: {self.url}")
                return False
            if response.status_code in [200, 301, 302, 307]:
                print(response.status_code)
                if not response.url == self.url:
                    self.url = response.url
                    print(f"Updated request url for {self.title}")
                parsed = feedparser.parse(response.content)
                for _entry in parsed.entries:
                    entry = Entry()
                    added = entry.parse_and_create(_entry, self.ID)
                    if added:
                        self.feed_last_update = datetime.datetime.fromtimestamp(
                            ts
                        ).strftime("%Y-%m-%d %H:%M:%S")
                if self.title is None:
                    self.title = parsed.feed.get("title")
                    print(f"updating title to: {parsed.feed.get('title')}")
                if self.description is None:
                    desc = parsed.feed.get("description", "")
                    if desc.length < 255:
                        self.description = desc
                        print(f"updating description to {desc}")

            elif response.status_code in [410, 404]:
                print(
                    "Erreur while fetching %s [%s]" % (self.url, response.status_code)
                )
                # self.active = 0
            else:
                print(f"{response.status_code} - Timeout?")
        self.last_update = datetime.datetime.fromtimestamp(ts).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.update()

    def harvest_all(self):
        feeds = self._get_all(harvest=True)
        if feeds:
            [self.harvest(feed[0]) for feed in feeds]

    def get_all(self, exclude_ids=None):
        if not exclude_ids:
            exclude_ids = []
        return self._get_all(exclude_ids=exclude_ids)

    def get_recents(self, amount=10, start=0):
        """
        get recent entries of any feed
        :param amount: (int) amount to fetch, defaults to 10
        :param start: (int) start, defaults to 0
        """
        cursor = self.db.connection.cursor()
        cursor.execute(
            "select feed.ID, entry.ID from entry "
            "left join feed on feed.ID = entry.feedID order by published desc limit ?, ?",
            (int(start), int(amount)),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_by_bookmarks(self, bookmarks):
        """
        expects a list of bookmarkrecords gets the feed and entries based on these
        """
        entries = [row[2] for row in bookmarks]
        if len(entries) == 0:
            return False
        fs = ",".join(["?"] * len(entries))  # template for in (?, ?, ? ...)
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(
                "select feed.ID, entry.ID, created_at from bookmark "
                "left join entry on bookmark.entryID = entry.ID "
                "left join feed on feed.ID = entry.feedID "
                "where entry.ID in (%s) order by bookmark.created_at desc" % fs,
                tuple(entries),
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except sqlite3.Error as e:
            print("sqlite Error: %s" % str(e))

    def _get(self, by=None, value=None):
        """
        get one feed by given method and value
        :param by: field to use in where
        :param value: value to be used for retrieval
        """
        if "ID" in by:
            self.db.cur.execute(
                "select ID, url, title, image, description, update_interval,feed_last_update, "
                "web_url, last_update, active, request_options from feed where ID = ?",
                (value,),
            )
        if "url" in by:
            self.db.cur.execute(
                "select ID, url, title, image, description, update_interval,feed_last_update, "
                "web_url, last_update, active, request_options from feed where url = ?",
                (value,),
            )

        row = self.db.cur.fetchone()
        if row:
            self.ID, self.url, self.title, self.image, self.description, self.update_interval, self.feed_last_update, self.web_url, self.last_update, self.active, self.request_options = (
                row
            )
        else:
            return False
        return True

    def _get_all(self, harvest=False, active=True, exclude_ids=None):
        """
        get all the active feeds
        :param harvest: Bool, if True only harvestable feeds are included
        :param active: Bool, defaults True, show only active feeds
        """
        if not exclude_ids:
            exclude_ids = []
        q = "select ID from feed where active = ?"
        if harvest:
            q += f" and last_update < datetime('now', 'localtime', '-59 minute') "
        if len(exclude_ids) > 0:
            q += " and ID not in ( %s )" % ",".join(exclude_ids)
        try:
            self.db.cur.execute(q, (active,))
        except sqlite3.Error as e:
            print("sqlite Error [x]: %s" % str(e))
            return False

        return self.db.cur.fetchall()

    def _parse_feed_data(self, feed):
        self.title = feed.title if hasattr(feed, "title") else None
        self.description = feed.sub_title if hasattr(feed, "sub_title") else None
        self.image = feed.image.get("href", None) if hasattr(feed, "image") else None

        if hasattr(feed, "links"):
            for link in feed.links:
                if (
                    link.get("type", None) == "text/html"
                    and link.get("rel", None) == "alternate"
                ):
                    self.web_url = link.href
            return True
        if not self.title and not self.description and not self.web_url:
            return False


def main():
    f = Feed()
    f.harvest(2)


if __name__ == "__main__":
    main()

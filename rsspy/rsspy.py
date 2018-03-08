# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask
from flask import render_template
from flask import request

from . import config
from model import feed as Feed
from model import entry as Entry


# setup basic config for the given log level
logging.basicConfig(level=('DEBUG' if config.DEBUG else config.LOG_LEVEL))

# setup flask app
app = Flask(__name__)
app.debug = True
if app.debug:
     app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def home():
    payload = render_template('home.html')
    return payload


@app.route("/feed/<identifier>")
def do_feed(identifier=None):

    amount = request.args.get('amount', 10)
    start = request.args.get('start', 0)

    if int(identifier):
        feed = Feed.Feed(int(identifier))
    else:
        feed = None
        # TODO: init_by_url (init_by('url', identifier) zoiets)
    # fill it
    feed.with_entries(amount=amount, start=start)
    payload = render_template("feed.html",
                              feed=feed,
                              amount=amount,
                              nextstart=int(start) + int(amount),
                              prevstart=max(int(start) - int(amount), -1)
                             )
    return payload

@app.route("/allfeeds")
def all_feeds():
    feed = Feed.Feed()
    feeds = feed.get_all()
    payload = '<ul class="feedlinks">'
    for f in feeds:
        actfeed = Feed.Feed(f)
        payload += render_template("menu/feedlink.html", feed=actfeed)
        print(actfeed.title)
    payload += '</ul>'
    return payload


@app.route("/recent")
def recent():
    f = Feed.Feed()
    recents = f.get_recents()
    feeds = {}
    for feedid, entryid in recents:
        if not feeds.get('feed%s' % feedid, None):
            feeds['feed%s' % feedid] = Feed.Feed(feedid)
        feeds['feed%s' % feedid].entries.append(Entry.Entry(entryid))

    print (feeds.values())
    return 'bundle'

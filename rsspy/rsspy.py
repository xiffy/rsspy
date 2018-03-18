# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask, request, render_template, session

from . import config
from model import feed as Feed
from model import entry as Entry
from model import user as User


# setup basic config for the given log level
logging.basicConfig(level=('DEBUG' if config.DEBUG else config.LOG_LEVEL))

# setup flask app
app = Flask(__name__)
app.debug = True
app.secret_key =  config.SESSION_KEY

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
    menu = all_feeds()

    if int(identifier):
        feed = Feed.Feed(int(identifier))
    else:
        feed = None
        # TODO: init_by_url (init_by('url', identifier) zoiets)
    # fill it
    feed.with_entries(amount=amount, start=start)
    payload = render_template("feed.html",
                              feed=feed,
                              menu=menu,
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
        #print(actfeed.title)
    payload += '</ul>'
    return payload


@app.route("/<username>/recent")
def logedin_recent(username):
    user = User.User()
    if user.verify(session['das_hash']):
        print('Welcome: %s (%s)' % (user.username, user.email))

    return recent()

@app.route("/recent")
def recent():

    amount = request.args.get('amount', 10)
    start = request.args.get('start', 0)
    menu = all_feeds()
    f = Feed.Feed()
    recents = f.get_recents(amount=amount, start=start)
    feeds = {}
    for feedid, entryid in recents:
        if not feeds.get('feed%s' % feedid, None):
            feeds['feed%s' % feedid] = Feed.Feed(feedid)
        feeds['feed%s' % feedid].entries.append(Entry.Entry(entryid))

    return render_template("recent.html",
                              feeds=feeds.values(),
                              amount=amount,
                              menu=menu,
                              nextstart=int(start) + int(amount),
                              prevstart=max(int(start) - int(amount), -1)
                              )


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = User.User()
        if user.do_login():
            session['das_hash'] = user.das_hash

    return render_template("login.html")

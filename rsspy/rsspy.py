# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask, request, render_template, session, jsonify

from . import config
from model import feed as Feed
from model import entry as Entry
from model import user as User
from model import group as Group
from model import bookmark as Bookmark


# setup basic config for the given log level
logging.basicConfig(level=('DEBUG' if config.DEBUG else config.LOG_LEVEL))

# setup flask app
app = Flask(__name__)
app.debug = True
app.secret_key =  config.SESSION_KEY

if app.debug:
     app.jinja_env.undefined = jinja2.StrictUndefined
     app.config['TEMPLATES_AUTO_RELOAD'] = True


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
    payload = '<h2><span class="simple-svg" data-icon="mdi-rss" data-inline="false"></span> feeds</h2><ul class="feedlinks">'
    for f in feeds:
        actfeed = Feed.Feed(f)
        payload += render_template("menu/feedlink.html", feed=actfeed)
        #print(actfeed.title)
    payload += '</ul>'
    return payload


@app.route("/<username>/recent")
def logedin_recent(username):
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        print('Welcome: %s (%s)' % (user.username, user.email))
    # this is a stub, this should personalize the view one day.
    return recent()

@app.route("/recent")
def recent():
    """
    Grabs x entries from the stash
    starting at pos y
    sorted chronological
    newest on top
    """
    amount = request.args.get('amount', 10)
    start = request.args.get('start', 0)
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
                              menu=all_feeds(),
                              nextstart=int(start) + int(amount),
                              path='/recent',
                              prevstart=max(int(start) - int(amount), -1)
                           )

@app.route("/user", methods=['GET', 'POST'])
def userpage():
    user = User.User()
    if not user.verify(session.get('das_hash', None)):
        return render_template("login.html")
    group = Group.Group()
    groups = group.get_groups(userID=user.ID)
    return render_template("userpage.html", user=user, groups=groups)

@app.route("/<username>/bookmarks")
def userbookmarks(username):
    if not username:
        redirect('/recent', 302)
    user = User.User(username=username)
    if user.ID:
        amount = request.args.get('amount', 10)
        start = request.args.get('start', 0)
        b = Bookmark.Bookmark()
        bookmarks = b.get_bookmarks(userID=user.ID, amount=amount, start=start)
        f = Feed.Feed()
        feedentries = f.get_by_bookmarks(bookmarks) if f.get_by_bookmarks(bookmarks) else []
        feeds = {}
        for feedid, entryid, d in feedentries:
            if not feeds.get('feed%s' % feedid, None):
                feeds['feed%s' % feedid] = Feed.Feed(feedid)
            feeds['feed%s' % feedid].entries.append(Entry.Entry(entryid))
        return render_template("recent.html",
                              feeds=feeds.values(),
                              amount=amount,
                              menu=all_feeds(),
                              path="/%s/bookmarks" % username,
                              nextstart=int(start) + int(amount),
                              prevstart=max(int(start) - int(amount), -1)
                    )

@app.route("/group/<groupid>")
def show_group(groupid):
    if not groupid:
        redirect('/recent', 302)
    group = Group.Group(ID=int(groupid))
    if not group.ID:
        redirect('/recent', 302)
    amount = request.args.get('amount', 10)
    start = request.args.get('start', 0)
    recents = group.get_recents(amount=amount, start=start)
    feeds = {}
    for feedid, entryid in recents:
        if not feeds.get('feed%s' % feedid, None):
            feeds['feed%s' % feedid] = Feed.Feed(feedid)
        feeds['feed%s' % feedid].entries.append(Entry.Entry(entryid))

    return render_template("recent.html",
                              feeds=feeds.values(),
                              amount=amount,
                              menu=all_feeds(),
                              nextstart=int(start) + int(amount),
                              path='/group/%s' % groupid,
                              prevstart=max(int(start) - int(amount), -1)
                           )


@app.route("/settings/feed/<id>", methods=['GET', 'POST'])
def maint_feed(id):
    f = Feed.Feed(int(id))
    return render_template("settings/feed.html", feed=f)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = User.User()
        if user.do_login():
            session['das_hash'] = user.das_hash
    return render_template("login.html")

@app.route("/bookmark/<entryID>", methods=['POST'])
def bookmark(entryID):
    result = {'error': 'Log in to use bookmark'}
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        result = Bookmark.Bookmark().add(userID=user.ID, entryID=entryID)
    return jsonify(result)

@app.route("/bookmark/<bookmarkID>", methods=['DELETE'])
def remove_bookmark(bookmarkID):
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        Bookmark.Bookmark(ID=int(bookmarkID)).delete()
    return ('', 204)

@app.route("/widget/feedlist")
def feedlist():
    exclude_ids = request.args.get('exclude', [])
    feeds = Feed.Feed().get_all(exclude_ids=exclude_ids)
    return ('hoi')


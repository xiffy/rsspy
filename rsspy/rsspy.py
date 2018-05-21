# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask, request, render_template, session, jsonify, redirect
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
from model import feed as Feed
from model import entry as Entry
from model import user as User
from model import group as Group
from model import group_feed as GroupFeed
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


@app.route("/feed/<identifier>", methods=['GET'])
def do_feed(identifier=None):
    amount = request.args.get('amount', 10)
    start = request.args.get('start', 0)
    menu = usermenu()
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
    payload = '<h2><span class="simple-svg" data-icon="mdi-rss"></span> feeds</h2><ul class="feedlinks">'
    for f in feeds:
        actfeed = Feed.Feed(f)
        payload += render_template("menu/feedlink.html", feed=actfeed)
        #print(actfeed.title)
    payload += '</ul>'
    return payload

def usermenu():
    user = User.User()
    payload = ''
    if user.verify(session.get('das_hash', None)):
        payload = render_template('menu/usermenu.html', user=user)
    return "%s %s" % (payload, all_feeds())


@app.route("/user/recent")
def logedin_recent():
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
                              menu=usermenu(),
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
    return render_template("userpage.html", user=user, groups=groups, menu=usermenu())

@app.route("/<username>/bookmarks")
def userbookmarks(username):
    if not username:
        return redirect('/recent', 302)
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
                              menu=usermenu(),
                              path="/%s/bookmarks" % username,
                              nextstart=int(start) + int(amount),
                              prevstart=max(int(start) - int(amount), -1)
                    )

@app.route("/group/<groupid>")
def show_group(groupid):
    if not groupid:
        return redirect('/recent', 302)
    group = Group.Group(ID=int(groupid))
    if not group.ID:
        return redirect('/recent', 302)
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
                              menu=usermenu(),
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
            return redirect("/user/recent", 302)
        else:
            print ('boe')
    return render_template("login.html")

@app.route("/bookmark/<entryID>", methods=['POST'])
def bookmark(entryID):
    result = {'error': 'Log in to use bookmark'}
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        result = Bookmark.Bookmark().add(userID=user.ID, entryID=entryID)
    return jsonify(result)

@app.route("/groupfeed/", methods=['POST'])
def groupfeed():
    result = {'error': 'no data'}
    if request.form.get('feedid') and request.form.get('groupid'):
        result = GroupFeed.GroupFeed(feedID=request.form.get('feedid'),
                                        groupID=request.form.get('groupid'))
    return jsonify(result)

@app.route("/bookmark/<bookmarkID>", methods=['DELETE'])
def remove_bookmark(bookmarkID):
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        Bookmark.Bookmark(ID=int(bookmarkID)).delete()
    return ('', 204)

@app.route("/groupfeed/<groupID>/<feedID>", methods=['DELETE'])
def remove_group_feed(groupID=None, feedID=None):
    GroupFeed.GroupFeed().delete(groupID=int(groupID), feedID=int(feedID))
    return ('', 204)

@app.route("/widget/feedlist")
def feedlist():
    exclude_ids = request.args.get('exclude', [])
    groupid = request.args.get('groupid', None)
    if groupid:
        group = Group.Group(int(groupid))
        feedids = [feed.ID for feed in group.feeds]
    else:
        group = Group.Group(description='Unknonw group')
        feedids = []
    f_ids = Feed.Feed().get_all(exclude_ids=group.feeds)
    feeds = [Feed.Feed(id) for id in f_ids]
    return render_template('widget/feedlist.html', feeds=feeds, group=group, feedids=feedids)

@app.route("/feed/add", methods=['POST'])
def create_feed():
    feed = Feed.Feed()
    new = feed.create(url=request.form.get('url'))
    return jsonify({'id': new.ID, 'url': new.url, 'title': new.title})

@app.route("/group/add", methods=['POST'])
def create_group():
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        aggregation = 'email' if request.form.get('aggregation') == 'true' else ''
        group = Group.Group(description=request.form.get('description'),
                            aggregation=aggregation,
                            frequency=request.form.get('frequency'),
                            userID=user.ID)

@app.route("/group/delete", methods=['DELETE'])
def delete_group():
    groupid = int(request.form.get('groupid'))
    if Group.Group(groupid).delete():
        return ('', 204)
    return ('error', 503)

@app.route("/send_digest", methods=['GET'])
def send_digest():
    digestables = Group.Group().get_digestables()
    for groupid in digestables:
        group = Group.Group(groupid)
        user = User.User(group.userID)
        digestable = group.get_digestable()
        if not digestable:
            continue
        feeds = {}
        for feedid, entryid in digestable:
            if not feeds.get('feed%s' % feedid, None):
                feeds['feed%s' % feedid] = Feed.Feed(feedid)
            feeds['feed%s' % feedid].entries.append(Entry.Entry(entryid))
        html = render_template("email.html",
                               feeds=feeds.values(),
                               group=group)
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Email digest: %s (issue: %s)" % (group.description, group.issue)
        msg['From'] = 'rsspy@xiffy.nl'
        msg['To'] = user.email
        text = 'switch to html'
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
        group.update_sent()
    return ('', 204)


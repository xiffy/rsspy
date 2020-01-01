# -*- coding: utf-8 -*-
import logging
import jinja2
from flask import Flask, request, render_template, session, jsonify, redirect, abort, url_for
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


def home():
    payload = render_template('home.html')
    return payload


def do_feed(identifier=None, outputtype='html'):
    """
    Get one feed from the database.
    grab @amount (int default: 10) of entries
    starting at position @start (int default: 0)
    add /xml to the path to get a rss feed generated here
    """
    if outputtype not in ['html', 'xml']:
        abort(404)

    template = 'feed.html' if outputtype == 'html' else 'rss.html'
    amount, start = amountstart()
    menu = usermenu()
    if int(identifier):
        feed = Feed.Feed(int(identifier))
    else:
        feed = None
        # TODO: init_by_url (init_by('url', identifier) zoiets)
    # fill it
    feed.with_entries(amount=amount, start=start)
    payload = render_template(template,
                              feed=feed,
                              menu=menu,
                              amount=amount,
                              nextstart=int(start) + int(amount),
                              prevstart=max(int(start) - int(amount), -1))
    if outputtype == 'html':
        return payload, 200, {'Cache-Control' : 's-maxage=10'}
    return payload, 200, {'Content-Type': 'text/xml; charset=utf-8', 'Cache-Control': 's-maxage=300'}


def all_feeds():
    feed = Feed.Feed()
    feeds = [Feed.Feed(f) for f in feed.get_all()]
    return render_template("menu/feedlink.html", feeds=feeds)


def logedin_recent():
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        print('Welcome: %s (%s)' % (user.username, user.email))
    # this is a stub, this should personalize the view one day.
    return recent()


def recent():
    """
    Grabs x entries from the stash
    starting at pos y
    sorted chronological
    newest on top
    """
    amount, start = amountstart()
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
                            prevstart=max(int(start) - int(amount), -1)), 200, {'Cache-Control' : 's-maxage=10'}


def userpage():
    user = User.User()
    if not user.verify(session.get('das_hash', None)):
        return render_template("login.html")
    group = Group.Group()
    groups = group.get_groups(userID=user.ID)
    return render_template("userpage.html", user=user, groups=groups, menu=usermenu())


def userbookmarks(username):
    if not username:
        return redirect('/recent', 302)
    user = User.User(username=username)
    if user.ID:
        amount, start = amountstart()

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
                               title='Bookmarks by: %s' % username,
                               path="/%s/bookmarks" % username,
                               nextstart=int(start) + int(amount),
                               prevstart=max(int(start) - int(amount), -1)), 200, {'Cache-Control': 's-maxage=1'}


def show_group(groupid):
    if not groupid:
        return redirect('/recent', 302)
    group = Group.Group(ID=int(groupid))
    if not group.ID:
        return redirect('/recent', 302)
    amount, start = amountstart()
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
                            title='Grouped feeds: %s' % group.description,
                            nextstart=int(start) + int(amount),
                            path='/group/%s' % groupid,
                            prevstart=max(int(start) - int(amount), -1)), 200, {'Cache-Control' : 's-maxage=30'}


def create_group():
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        aggregation = 'email' if request.form.get('aggregation') == 'true' else ''
        group = Group.Group(description=request.form.get('description'),
                            aggregation=aggregation,
                            frequency=request.form.get('frequency'),
                            userID=user.ID)


def remove_group():
    groupid = int(request.form.get('groupid'))
    if Group.Group(groupid).delete():
        return '', 204
    return 'error', 503


def groupfeed():
    result = {'error': 'no data'}
    if request.form.get('feedid') and request.form.get('groupid'):
        result = GroupFeed.GroupFeed(feedID=request.form.get('feedid'), groupID=request.form.get('groupid'))
    return jsonify(result)


def remove_groupfeed(groupID=None, feedID=None):
    GroupFeed.GroupFeed().delete(groupID=int(groupID), feedID=int(feedID))
    return ('', 204)


def maint_feed(id):
    f = Feed.Feed(int(id))
    return render_template("settings/feed.html", feed=f)


def feedlist():
    groupid = request.args.get('groupid', None)
    if groupid:
        group = Group.Group(int(groupid))
        feedids = [feed.ID for feed in group.feeds]
    else:
        group = Group.Group(description='Unknonw group')
        feedids = []
    f_ids = Feed.Feed().get_all()
    feeds = [Feed.Feed(id) for id in f_ids]
    return render_template('widget/feedlist.html', feeds=feeds, group=group, feedids=feedids), 200, {'Cache-Control' : 's-maxage=0'}


def create_feed():
    feed = Feed.Feed()
    new = feed.create(url=request.form.get('url'))
    return jsonify({'id': new.ID, 'url': new.url, 'title': new.title})


def login():
    if request.method == "POST":
        user = User.User()
        if user.do_login():
            session['das_hash'] = user.das_hash
            return redirect('https://rss.xiffy.nl/recent', 302)
        else:
            print ('boe')
    return render_template("login.html")


def bookmark(entryID):
    result = {'error': 'Log in to use bookmark'}
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        result = Bookmark.Bookmark().add(userID=user.ID, entryID=entryID)
    return jsonify(result)


def remove_bookmark(bookmarkID):
    user = User.User()
    if user.verify(session.get('das_hash', None)):
        Bookmark.Bookmark(ID=int(bookmarkID)).delete()
    return ('', 204)


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
        print('sent digest to: %s. %s' % (user.email, group.description))
    return ('', 204)


def search():
    amount, start = amountstart()
    tokens = request.args.get('q', '')
    if not tokens:
        return recent()
    e = Entry.Entry()
    hits = e.search(tokens, amount=amount, start=start)
    feeds = {}

    for feedid, entryid, d, score in hits:
        if not feeds.get('feed%s' % feedid, None):
            feeds['feed%s' % feedid] = Feed.Feed(feedid)
        feeds['feed%s' % feedid].entries.append(Entry.Entry(entryid))
    return render_template("recent.html",
                           feeds=feeds.values(),
                           amount=amount,
                           menu=usermenu(),
                           title='Search: %s' % tokens,
                           path="/search",
                           extraarg="&q=%s" % tokens,
                           nextstart=int(start) + int(amount),
                           prevstart=max(int(start) - int(amount), -1),
                           tokens=tokens,
                           totresults= e.searchamount(q=tokens)), 200, {'Cache-Control': 's-maxage=1'}

def amountstart():
    amount = request.args.get('amount', 10)
    start = request.args.get('start', 0)
    try:
        amount = int(amount)
        start = int(start)
    except ValueError as e:
        abort(400)
    return amount, start


def usermenu():
    user = User.User()
    payload = ''
    if user.verify(session.get('das_hash', None)):
        groups = Group.Group().get_groups(userID=user.ID)
        if not groups:
            groups = []
        payload = render_template('menu/usermenu.html', user=user, groups=groups)
    return "%s %s" % (payload, all_feeds())


def create_rsspy():
    # setup flask app
    app = Flask('rsspy')
    #print(__name__)
    app.debug = True
    app.secret_key =  config.SESSION_KEY
    app.add_url_rule('/',view_func=home)
    app.add_url_rule('/feed/<int:identifier>', methods=['GET'], view_func=do_feed)
    app.add_url_rule("/feed/<int:identifier>/<outputtype>", methods=['GET'], view_func=do_feed)
    app.add_url_rule('/allfeeds', view_func=all_feeds)
    app.add_url_rule('/user/recent', view_func=logedin_recent)
    app.add_url_rule('/recent', view_func=recent)
    app.add_url_rule('/user', view_func=userpage, methods=['GET', 'POST'])
    app.add_url_rule('/<username>/bookmarks', view_func=userbookmarks)
    app.add_url_rule('/group/<int:groupid>', view_func=show_group)
    app.add_url_rule('/settings/feed/<int:id>', view_func=maint_feed, methods=['GET', 'POST'])
    app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/bookmark/<entryID>', view_func=bookmark, methods=['POST'])
    app.add_url_rule('/bookmark/<bookmarkID>', view_func=remove_bookmark, methods=['DELETE'])
    app.add_url_rule('/groupfeed/', view_func=groupfeed, methods=['POST'])
    app.add_url_rule('/groupfeed/<groupID>/<feedID>', view_func=remove_groupfeed, methods=['DELETE'])
    app.add_url_rule('/group/add', view_func=create_group, methods=['POST'])
    app.add_url_rule('/group/delete', view_func=remove_group,  methods=['DELETE'])
    app.add_url_rule('/widget/feedlist', view_func=feedlist)
    app.add_url_rule('/feed/add', view_func=create_feed, methods=['POST'])
    app.add_url_rule('/send_digest', view_func=send_digest,methods=['GET'])
    app.add_url_rule('/search', view_func=search, methods=['GET'])

    #app.config['SERVER_NAME'] = 'rss.xiffy.nl'

    return app

app = create_rsspy()


if app.debug:
    app.jinja_env.undefined = jinja2.StrictUndefined
    app.config['TEMPLATES_AUTO_RELOAD'] = True



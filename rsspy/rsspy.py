# -*- coding: utf-8 -*-
import logging
import jinja2
from flask import Flask, request, render_template, session, jsonify, redirect, abort
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import Config
from .model.feed import Feed
from .model.entry import Entry
from .model.user import User
from .model.group import Group
from .model.group_feed import GroupFeed
from .model.bookmark import Bookmark


# setup basic config for the given log level
logging.basicConfig(level=("DEBUG" if Config.DEBUG.value else Config.LOG_LEVEL.value))


def home():
    payload = render_template("home.html")
    return payload


def do_feed(identifier=None, outputtype="html"):
    """
    Get one feed from the database.
    grab @amount (int default: 10) of entries
    starting at position @start (int default: 0)
    add /xml to the path to get a rss feed generated here
    """
    if outputtype not in ["html", "xml"]:
        abort(404)

    template = "feed.html" if outputtype == "html" else "rss.html"
    amount, start = amountstart()
    menu = usermenu()
    if int(identifier):
        feed = Feed(int(identifier))
    else:
        feed = None
        # TODO: init_by_url (init_by('url', identifier) zoiets)
    # fill it
    feed.with_entries(amount=amount, start=start)
    payload = render_template(
        template,
        feed=feed,
        menu=menu,
        amount=amount,
        nextstart=int(start) + int(amount),
        prevstart=max(int(start) - int(amount), -1),
    )
    if outputtype == "html":
        return payload, 200, {"Cache-Control": "s-maxage=10"}
    return (
        payload,
        200,
        {"Content-Type": "text/xml; charset=utf-8", "Cache-Control": "s-maxage=300"},
    )


def all_feeds():
    feed = Feed()
    feeds = [Feed(f[0]) for f in feed.get_all()]
    return render_template("menu/feedlink.html", feeds=feeds)


def logedin_recent():
    user = User()
    if user.verify(session.get("das_hash", None)):
        print("Welcome: %s (%s)" % (user.username, user.email))
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
    f = Feed()
    recents = f.get_recents(amount=amount, start=start)
    feeds = {}
    for feedid, entryid in recents:
        if not feeds.get("feed%s" % feedid, None):
            feeds["feed%s" % feedid] = Feed(feedid)
        feeds["feed%s" % feedid].entries.append(Entry(entryid))

    return (
        render_template(
            "recent.html",
            feeds=feeds.values(),
            amount=amount,
            menu=usermenu(),
            nextstart=int(start) + int(amount),
            path="/recent",
            prevstart=max(int(start) - int(amount), -1),
        ),
        200,
        {"Cache-Control": "s-maxage=10"},
    )


def userpage():
    user = User()
    if not user.verify(session.get("das_hash", None)):
        return render_template("login.html")
    group = Group()
    groups = group.get_groups(userID=user.ID)
    return render_template("userpage.html", user=user, groups=groups, menu=usermenu())


def userbookmarks(username):
    if not username:
        return redirect("/recent", 302)
    user = User(username=username)
    if user.ID:
        amount, start = amountstart()

        b = Bookmark()
        bookmarks = b.get_bookmarks(userID=user.ID, amount=amount, start=start)
        f = Feed()
        feedentries = (
            f.get_by_bookmarks(bookmarks) if f.get_by_bookmarks(bookmarks) else []
        )
        feeds = {}
        for feedid, entryid, d in feedentries:
            if not feeds.get("feed%s" % feedid, None):
                feeds["feed%s" % feedid] = Feed(feedid)
            feeds["feed%s" % feedid].entries.append(Entry(entryid))
        return (
            render_template(
                "recent.html",
                feeds=feeds.values(),
                amount=amount,
                menu=usermenu(),
                title="Bookmarks by: %s" % username,
                path="/%s/bookmarks" % username,
                nextstart=int(start) + int(amount),
                prevstart=max(int(start) - int(amount), -1),
            ),
            200,
            {"Cache-Control": "s-maxage=1"},
        )


def show_group(groupid):
    if not groupid:
        return redirect("/recent", 302)
    group = Group(ID=int(groupid))
    if not group.ID:
        return redirect("/recent", 302)
    amount, start = amountstart()
    recents = group.get_recents(amount=amount, start=start)
    feeds = {}
    for feedid, entryid in recents:
        if not feeds.get("feed%s" % feedid, None):
            feeds["feed%s" % feedid] = Feed(feedid)
        feeds["feed%s" % feedid].entries.append(Entry(entryid))

    return (
        render_template(
            "recent.html",
            feeds=feeds.values(),
            amount=amount,
            menu=usermenu(),
            title="Grouped feeds: %s" % group.description,
            nextstart=int(start) + int(amount),
            path="/group/%s" % groupid,
            prevstart=max(int(start) - int(amount), -1),
        ),
        200,
        {"Cache-Control": "s-maxage=30"},
    )


def create_group():
    user = User()
    if user.verify(session.get("das_hash", None)):
        aggregation = "email" if request.form.get("aggregation") == "true" else ""
        group = Group(
            description=request.form.get("description"),
            aggregation=aggregation,
            frequency=request.form.get("frequency"),
            userID=user.ID,
        )


def remove_group():
    groupid = int(request.form.get("groupid"))
    if Group(groupid).delete():
        return "", 204
    return "error", 503


def groupfeed():
    result = {"error": "no data"}
    if request.form.get("feedid") and request.form.get("groupid"):
        result = GroupFeed(
            feedID=request.form.get("feedid"), groupID=request.form.get("groupid")
        )
    return jsonify(result.ID)


def remove_groupfeed(groupID=None, feedID=None):
    GroupFeed().delete(groupID=int(groupID), feedID=int(feedID))
    return ("", 204)


def maint_feed(id):
    f = Feed(int(id))
    return render_template("settings/feed.html", feed=f)


def feedlist():
    groupid = request.args.get("groupid", None)
    if groupid:
        group = Group(int(groupid))
        feedids = [feed.ID for feed in group.feeds]
    else:
        group = Group(description="Unknonw group")
        feedids = []
    f_ids = Feed().get_all()
    feeds = [Feed(id[0]) for id in f_ids]
    return (
        render_template(
            "widget/feedlist.html", feeds=feeds, group=group, feedids=feedids
        ),
        200,
        {"Cache-Control": "s-maxage=0"},
    )


def create_feed():
    feed = Feed()
    print(request.form.get("url", "PitjePuk"))
    new = feed.create(url=request.form.get("url"))
    return jsonify(
        {
            "id": new.ID,
            "url": new.url,
            "title": new.title,
            "formurl": request.form.get("url"),
        }
    )


def login():
    if request.method == "POST":
        user = User()
        if user.do_login():
            session["das_hash"] = user.das_hash
            return redirect("https://rss.xiffy.nl/recent", 302)
        else:
            print("boe")
    return render_template("login.html")


def bookmark(entryID):
    result = {"error": "Log in to use bookmark"}
    user = User()
    if user.verify(session.get("das_hash", None)):
        result = Bookmark().add(userID=user.ID, entryID=entryID)
    return jsonify(result)


def remove_bookmark(bookmarkID):
    user = User()
    if user.verify(session.get("das_hash", None)):
        Bookmark(ID=int(bookmarkID)).delete()
    return ("", 204)


def send_digest():
    digestables = Group().get_digestables()
    ret = ""
    for (groupid,) in digestables:
        group = Group(groupid)
        user = User(group.userID)
        digestable = group.get_digestable()
        if not digestable:
            continue
        feeds = {}
        ret = str(digestable)
        for feedid, entryid in digestable:
            if not feeds.get("feed%s" % feedid, None):
                feeds["feed%s" % feedid] = Feed(feedid)
            feeds["feed%s" % feedid].entries.append(Entry(entryid))
        html = render_template("email.html", feeds=feeds.values(), group=group)
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Email digest: %s (issue: %s)" % (
            group.description,
            group.issue,
        )
        msg["From"] = "rsspy@xiffy.nl"
        msg["To"] = user.email
        text = "switch to html"
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))
        s = smtplib.SMTP("localhost")
        s.sendmail(msg["From"], msg["To"], msg.as_string())
        s.quit()
        group.update_sent()
        print("sent digest to: %s. %s" % (user.email, group.description))
    return ("", 204)


def search():
    amount, start = amountstart()
    tokens = request.args.get("q", "")
    if not tokens:
        return recent()
    e = Entry()
    hits = e.search(tokens, amount=amount, start=start)
    feeds = {}
    for feedid, entryid, title, description, contents in hits:
        if not feeds.get("feed%s" % feedid, None):
            feeds["feed%s" % feedid] = Feed(feedid)
        feeds["feed%s" % feedid].entries.append(Entry(entryid))
    return (
        render_template(
            "recent.html",
            feeds=feeds.values(),
            amount=amount,
            menu=usermenu(),
            title="Search: %s" % tokens,
            path="/search",
            extraarg="&q=%s" % tokens,
            nextstart=int(start) + int(amount),
            prevstart=max(int(start) - int(amount), -1),
            tokens=tokens,
            totresults=0,
            # totresults=e.searchamount(q=tokens),
        ),
        200,
        {"Cache-Control": "s-maxage=1"},
    )


def amountstart():
    amount = request.args.get("amount", 10)
    start = request.args.get("start", 0)
    try:
        amount = int(amount)
        start = int(start)
    except ValueError as e:
        abort(400)
    return amount, start


def usermenu():
    user = User()
    payload = ""
    if user.verify(session.get("das_hash", None)):
        groups = Group().get_groups(userID=user.ID)
        if not groups:
            groups = []
        payload = render_template("menu/usermenu.html", user=user, groups=groups)
    return "%s %s" % (payload, all_feeds())


def create_rsspy():
    # setup flask app
    app = Flask(
        "rsspy",
        template_folder=f"{Config.PROJECT_ROOT.value}/rsspy/templates",
        static_folder=f"{Config.PROJECT_ROOT.value}/rsspy/static",
    )
    app.debug = True
    app.secret_key = Config.SESSION_KEY.value
    app.add_url_rule("/", view_func=home)
    app.add_url_rule("/feed/<int:identifier>", methods=["GET"], view_func=do_feed)
    app.add_url_rule(
        "/feed/<int:identifier>/<outputtype>", methods=["GET"], view_func=do_feed
    )
    app.add_url_rule("/allfeeds", view_func=all_feeds)
    app.add_url_rule("/user/recent", view_func=logedin_recent)
    app.add_url_rule("/recent", view_func=recent)
    app.add_url_rule("/user", view_func=userpage, methods=["GET", "POST"])
    app.add_url_rule("/<username>/bookmarks", view_func=userbookmarks)
    app.add_url_rule("/group/<int:groupid>", view_func=show_group)
    app.add_url_rule(
        "/settings/feed/<int:id>", view_func=maint_feed, methods=["GET", "POST"]
    )
    app.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
    app.add_url_rule("/bookmark/<entryID>", view_func=bookmark, methods=["POST"])
    app.add_url_rule(
        "/bookmark/<bookmarkID>", view_func=remove_bookmark, methods=["DELETE"]
    )
    app.add_url_rule("/groupfeed/", view_func=groupfeed, methods=["POST"])
    app.add_url_rule(
        "/groupfeed/<groupID>/<feedID>", view_func=remove_groupfeed, methods=["DELETE"]
    )
    app.add_url_rule("/group/add", view_func=create_group, methods=["POST"])
    app.add_url_rule("/group/delete", view_func=remove_group, methods=["DELETE"])
    app.add_url_rule("/widget/feedlist", view_func=feedlist)
    app.add_url_rule("/feed/add", view_func=create_feed, methods=["POST"])
    app.add_url_rule("/send_digest", view_func=send_digest, methods=["GET"])
    app.add_url_rule("/search", view_func=search, methods=["GET"])

    # app.config['SERVER_NAME'] = 'rss.xiffy.nl'

    return app


app = create_rsspy()


if app.debug:
    app.jinja_env.undefined = jinja2.StrictUndefined
    app.config["TEMPLATES_AUTO_RELOAD"] = True

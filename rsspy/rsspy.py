# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask
from flask import render_template
from . import config
from model import feed as Feed


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

    if int(identifier):
        feed = Feed.Feed(int(identifier))
    else:
        feed = None
        # TODO: init_by_url (init_by('url', identifier) zoiets)
    # fill it
    feed.with_entries(amount=10, start=0)
    payload = render_template("feed.html", feed=feed)
    return payload




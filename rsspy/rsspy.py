# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask
import config

# setup basic config for the given log level
logging.basicConfig(level=('DEBUG' if config.DEBUG else config.LOG_LEVEL))

# setup flask app
app = Flask(__name__)

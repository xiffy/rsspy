#!/bin/bash
export FLASK_DEBUG=1
FLASK_APP=rsspy.py flask run --port=5003 --host=0.0.0.0

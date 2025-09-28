"""Extremely basic mostly static HTML front end"""

from flask import Flask, render_template
import requests

COMHAIRIMH_API = 'http://127.0.0.1:8000/'  # TODO env

app = Flask(__name__)

@app.route("/")
def home():
    """home page with all timers"""
    result = requests.get(COMHAIRIMH_API + 'countdowns/', timeout=5)
    result.raise_for_status()
    data = result.json()
    return render_template('basic.html', timers=data['countdowns'])

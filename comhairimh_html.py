"""Extremely basic mostly static HTML front end"""

import datetime
from flask import Flask, render_template, request, redirect, url_for
import requests

COMHAIRIMH_API = 'http://127.0.0.1:8000/'  # TODO env

app = Flask(__name__)

@app.route("/")
def home():
    """home page with all timers"""
    result = requests.get(COMHAIRIMH_API + 'countdowns/', timeout=5)
    result.raise_for_status()
    data = result.json()
    server_time = datetime.datetime.fromisoformat(data['time'])
    # TODO auto-refresh time period
    return render_template('basic.html',
                           timers=data['countdowns'],
                           time=server_time.strftime('%H:%M'))
@app.post('/add')
def add_timer():
    """Add a timer or start a pomodoro"""
    if request.form.get('pom'):
        res = requests.post(COMHAIRIMH_API + 'pomodoros/',
                            timeout=5,
                            json={'pomodoro_type': 'next'})
        res.raise_for_status()
        return redirect(url_for('home'))
    res = requests.post(COMHAIRIMH_API + 'countdowns/',
                        timeout=5,
                        json={'label': request.form.get('label'),
                              'deadline': datetime.datetime.combine(datetime.date.today(),
                                                                    datetime.time.fromisoformat(request.form.get('deadline'))).isoformat()})
    res.raise_for_status()
    return redirect(url_for('home'))

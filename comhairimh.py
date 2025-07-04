"""Comhairimh API"""

import datetime
#from typing import Optional
from fastapi import FastAPI  #, Depends, HTTPException
from pydantic import BaseModel

AUTO_ACK = 300


class Countdown(BaseModel):
    """A single countdown"""
    label: str
    deadline: datetime.datetime

    def output(self):
        """Output countdown with time remaining"""
        now = datetime.datetime.now()
        return {'label': self.label,
                'deadline': self.deadline,
                'remaining': int((self.deadline - now).total_seconds() / 60)}

app = FastAPI(title="Comhairimh API")

#countdowns = [Countdown(label="Test",
#                        deadline=datetime.datetime.now() + datetime.timedelta(minutes=25))]
countdowns = []

@app.get("/countdowns/")
def get_list():
    """Get top active countdowns"""
    return {'time': datetime.datetime.now(),
            'countdowns': [x.output() for x in countdowns]}

@app.post("/countdowns/")
def add_countdown(countdown: Countdown):
    """Add a new countdown"""
    countdowns.append(countdown)
    return countdown.output()

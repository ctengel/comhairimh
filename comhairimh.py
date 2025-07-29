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
    # TODO catalog start time
    #start_time: datetime.datetime

    def output(self):
        """Output countdown with time remaining"""
        now = datetime.datetime.now()
        remaining = max(int((self.deadline - now).total_seconds() / 60), 0)
        return {'label': self.label,
                'deadline': self.deadline,
                'remaining': remaining}

    def is_ack(self):
        """True if countdown has been acknowledged"""
        return (datetime.datetime.now() - self.deadline).total_seconds() > AUTO_ACK


app = FastAPI(title="Comhairimh API")

#countdowns = [Countdown(label="Test",
#                        deadline=datetime.datetime.now() + datetime.timedelta(minutes=25))]
countdowns = []

@app.get("/countdowns/")
def get_list():
    """Get top active countdowns"""
    return {'time': datetime.datetime.now(),
            'countdowns': [x.output() for x in countdowns if not x.is_ack()]}

@app.post("/countdowns/")
def add_countdown(countdown: Countdown):
    """Add a new countdown"""
    countdowns.append(countdown)
    return countdown.output()

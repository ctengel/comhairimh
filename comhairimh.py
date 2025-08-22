"""Comhairimh API"""

import datetime
import enum
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


class PomodoroType(str, enum.Enum):
    """Types of pomodoros"""
    work = "work"
    break_ = "break"
    next_ = "next"

class Pomodoro(BaseModel):
    """A pomodoro request"""
    pomodoro_type: PomodoroType


app = FastAPI(title="Comhairimh API")

#countdowns = [Countdown(label="Test",
#                        deadline=datetime.datetime.now() + datetime.timedelta(minutes=25))]
countdowns = []
current_pom = None

@app.get("/countdowns/")
def get_list():
    """Get top active countdowns"""
    return {'time': datetime.datetime.now(),
            'countdowns': sorted([x.output() for x in countdowns if not x.is_ack()],
                                 key=lambda y: y['remaining'])}

@app.post("/countdowns/")
def add_countdown(countdown: Countdown):
    """Add a new countdown"""
    countdowns.append(countdown)
    return countdown.output()

@app.post("/pomodoros/")
def start_pomodoro(pomodoro: Pomodoro):
    """Start a pomodoro"""
    global current_pom
    if pomodoro.pomodoro_type == PomodoroType.next_:
        pomodoro.pomodoro_type = PomodoroType.work
        if current_pom and current_pom.pomodoro_type == PomodoroType.work:
            pomodoro.pomodoro_type = PomodoroType.break_
    length = 25
    if pomodoro.pomodoro_type == PomodoroType.break_:
        length = 5
    deadline = datetime.datetime.now() + datetime.timedelta(minutes=length)
    current_pom = pomodoro
    countdown = Countdown(label=f"{pomodoro.pomodoro_type.value} pomodoro",
                          deadline=deadline)
    countdowns.append(countdown)
    return countdown.output()

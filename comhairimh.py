"""Comhairimh API"""

import datetime
import enum
import itertools
#from typing import Optional
from fastapi import FastAPI, HTTPException  #, Depends
from pydantic import BaseModel

AUTO_ACK = 300


class Countdown(BaseModel):
    """A single countdown"""
    label: str
    deadline: datetime.datetime
    id: int | None = None
    acked: bool = False
    # TODO catalog start time
    #start_time: datetime.datetime

    def output(self):
        """Output countdown with time remaining"""
        now = datetime.datetime.now()
        remaining = max(int((self.deadline - now).total_seconds() / 60), 0)
        return {'id': self.id,
                'label': self.label,
                'deadline': self.deadline,
                'remaining': remaining}

    def is_ack(self):
        """True if countdown has been acknowledged"""
        return self.acked or (datetime.datetime.now() - self.deadline).total_seconds() > AUTO_ACK


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
countdown_ids = itertools.count(1)
current_pom = None
current_pom_countdown = None

def register_countdown(countdown):
    """Assign an ID to a countdown and add it to the list"""
    countdown.id = next(countdown_ids)
    countdowns.append(countdown)

@app.get("/countdowns/")
def get_list():
    """Get top active countdowns"""
    return {'time': datetime.datetime.now(),
            'countdowns': sorted([x.output() for x in countdowns if not x.is_ack()],
                                 key=lambda y: y['remaining'])}

@app.post("/countdowns/")
def add_countdown(countdown: Countdown):
    """Add a new countdown"""
    register_countdown(countdown)
    return countdown.output()

@app.post("/countdowns/{countdown_id}/ack")
def ack_countdown(countdown_id: int):
    """Acknowledge a countdown"""
    for countdown in countdowns:
        if countdown.id == countdown_id:
            countdown.acked = True
            return countdown.output()
    raise HTTPException(status_code=404, detail="Countdown not found")

@app.post("/pomodoros/")
def start_pomodoro(pomodoro: Pomodoro):
    """Start a pomodoro"""
    global current_pom, current_pom_countdown
    if pomodoro.pomodoro_type == PomodoroType.next_:
        pomodoro.pomodoro_type = PomodoroType.work
        if current_pom and current_pom.pomodoro_type == PomodoroType.work:
            pomodoro.pomodoro_type = PomodoroType.break_
    length = 25
    if pomodoro.pomodoro_type == PomodoroType.break_:
        length = 5
    deadline = datetime.datetime.now() + datetime.timedelta(minutes=length)
    current_pom = pomodoro
    if current_pom_countdown:
        current_pom_countdown.acked = True
    countdown = Countdown(label=f"{pomodoro.pomodoro_type.value} pomodoro",
                          deadline=deadline)
    register_countdown(countdown)
    current_pom_countdown = countdown
    return countdown.output()

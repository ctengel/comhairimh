"""Countdown TUI

From https://textual.textualize.io/tutorial/
"""

from time import monotonic
import datetime

from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header, Label, Input
from textual.screen import ModalScreen
import requests

API_URL = "http://127.0.0.1:8000"
API_REFRESH = 60

def get_countdowns():
    """Get current countdowns from API"""
    return requests.get(API_URL + "/countdowns/").json()["countdowns"]

def add_countdown(countdown_string, countdown_list):
    """Add a new countdown to the list"""
    (count_time, _, count_label) = countdown_string.partition(' ')
    requests.post(API_URL + "/countdowns/",
                  json={'label': count_label,
                        'deadline': datetime.datetime.combine(datetime.date.today(),
                                                              datetime.time.fromisoformat(count_time)).isoformat()})
    countdown_list.reload()


class CardEdit(ModalScreen[str]):
    """Ask user for text of card"""

    def compose(self) -> ComposeResult:
        yield Input()

    def on_input_submitted(self) -> None:
        """Exit screen with input value"""
        self.dismiss(self.query_one(Input).value)


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    end_time = reactive(datetime.datetime.now())
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1, self.update_time)  #, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = (self.end_time - datetime.datetime.now()).total_seconds()

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:02.0f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(Horizontal):
    """A stopwatch widget."""

    my_name = reactive("")
    end_time = reactive(datetime.datetime.now())

#    def on_button_pressed(self, event: Button.Pressed) -> None:
#        """Event handler called when a button is pressed."""
#        button_id = event.button.id
#        time_display = self.query_one(TimeDisplay)
#        if button_id == "start":
#            time_display.start()
#            self.add_class("started")
#        elif button_id == "stop":
#            time_display.stop()
#            self.remove_class("started")
#        elif button_id == "reset":
#            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
 #       yield Button("Start", id="start", variant="success")
 #       yield Button("Stop", id="stop", variant="error")
 #       yield Button("Reset", id="reset")
        yield Label(self.my_name)
        my_time = TimeDisplay()
        my_time.end_time = self.end_time
        yield my_time

class Clock(Digits):
    """A clock that just shows the current time"""

    time = reactive(datetime.datetime.now)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.set_interval(1, self.update_time)  #, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = datetime.datetime.now()
        self.update(f"{self.time.hour:02,.0f}:{self.time.minute:02.0f}")

class CountdownClocks(VerticalScroll):
    """A group of countdown timers"""

    def compose(self):
        """Add timers"""
        for countdown in get_countdowns():
            new_countdown = Stopwatch()
            new_countdown.my_name = countdown["label"]
            new_countdown.end_time = datetime.datetime.fromisoformat(countdown["deadline"])
            yield new_countdown

    def reload(self):
        """Reload the entire list from API"""
        self.refresh(recompose=True)

    def on_mount(self):
        """Set refresh time"""
        self.set_interval(API_REFRESH, self.reload)


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"

    BINDINGS = [
        ("a", "add_stopwatch", "Add"),
#        ("r", "remove_stopwatch", "Remove"),
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        my_scroll = CountdownClocks(id="timers")
        #for countdown in get_countdowns():
        #    add_countdown(my_scroll, countdown)
        yield Vertical(my_scroll, Clock())


    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        tgt_list = self.query_one(CountdownClocks)

        def add_card_callback(card_text: str | None) -> None:
            """Called when card edit completes"""
            add_countdown(card_text, tgt_list)

        self.push_screen(CardEdit(), add_card_callback)

#    def action_remove_stopwatch(self) -> None:
#        """Called to remove a timer."""
#        timers = self.query("Stopwatch")
#        if timers:
#            timers.last().remove()


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()

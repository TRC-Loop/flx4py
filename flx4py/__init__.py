"""
flx4py — Python library for the Pioneer DDJ-FLX4 DJ controller.

Typical usage::

    import flx4py

    controller = flx4py.DDJFlx4()

    @controller.on_pad(deck=1, pressed=True)
    def pad_pressed(event: flx4py.PadEvent):
        controller.leds.set_pad(event.deck, event.pad, True)
        print(f"Pad {event.pad} on deck {event.deck}")

    with controller:
        import time
        while True:
            time.sleep(1)
"""

from .controller import DDJFlx4
from .events import (
    BrowseEvent,
    ButtonEvent,
    JogEvent,
    JogTouchEvent,
    KnobEvent,
    PadEvent,
    TabEvent,
)
from .leds import LEDController, LEDState, PadMode

__version__ = "0.1.0"

__all__ = [
    "DDJFlx4",
    "LEDController",
    "LEDState",
    "PadMode",
    "PadEvent",
    "TabEvent",
    "ButtonEvent",
    "KnobEvent",
    "JogEvent",
    "JogTouchEvent",
    "BrowseEvent",
]

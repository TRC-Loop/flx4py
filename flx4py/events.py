"""
Event dataclasses emitted by the DDJFlx4 controller.

Each event type corresponds to a physical interaction with the controller.
All events are dispatched to registered callbacks in the background listener
thread, so keep callbacks fast or offload heavy work to another thread.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PadEvent:
    """A performance pad was pressed or released."""
    deck: int
    """Deck number (1 or 2)."""
    pad: int
    """Pad index 0–7 (left to right)."""
    pressed: bool
    """``True`` on press, ``False`` on release."""
    velocity: int
    """Raw MIDI velocity (0–127)."""


@dataclass(frozen=True)
class TabEvent:
    """A pad-mode tab key (HOT CUE / PAD FX / BEAT JUMP / SAMPLER) was pressed or released."""
    deck: int
    """Deck number (1 or 2)."""
    tab: int
    """Tab index: 0 = HOT CUE, 1 = PAD FX, 2 = BEAT JUMP, 3 = SAMPLER."""
    pressed: bool
    """``True`` on press, ``False`` on release."""


@dataclass(frozen=True)
class ButtonEvent:
    """A named button was pressed or released."""
    name: str
    """Button identifier string, e.g. ``'PLAY_PAUSE'``, ``'CUE'``, ``'BEAT_SYNC'``."""
    deck: int | None
    """Deck number (1 or 2), or ``None`` for global buttons (FX, mixer, browse)."""
    shifted: bool
    """``True`` when the SHIFT key was held at the time of the event."""
    pressed: bool
    """``True`` on press, ``False`` on release."""


@dataclass(frozen=True)
class KnobEvent:
    """An absolute knob or fader changed value.

    Covers channel faders, EQ knobs, trim, CFX, master level, crossfader,
    headphone mix/level, mic level, smart fader, FX level, and the
    mono/stereo slider.

    For ``TEMPO``, ``value`` is in the range ``-1.0`` (slowest) to ``+1.0``
    (fastest) with ``0.0`` at center. All other controls use ``0.0``–``1.0``.
    """
    name: str
    """Control name, e.g. ``'CH_FADER'``, ``'CROSSFADER'``, ``'EQ_HI'``."""
    deck: int | None
    """Deck number (1 or 2), or ``None`` for global controls."""
    value: float
    """Normalised value. See class docstring for ranges."""
    raw: int
    """Raw 14-bit (0–16383) or 7-bit (0–127) MIDI value before normalisation."""


@dataclass(frozen=True)
class JogEvent:
    """The jog wheel was rotated."""
    deck: int
    """Deck number (1 or 2)."""
    surface: str
    """``'top'`` (platter surface) or ``'side'`` (outer ring)."""
    direction: int
    """``+1`` for clockwise / right, ``-1`` for counter-clockwise / left."""
    velocity: int
    """Magnitude of the turn (number of encoder steps, usually 1)."""


@dataclass(frozen=True)
class JogTouchEvent:
    """The jog wheel platter was touched or released."""
    deck: int
    """Deck number (1 or 2)."""
    touched: bool
    """``True`` when touched, ``False`` when released."""


@dataclass(frozen=True)
class BrowseEvent:
    """The browse encoder was rotated."""
    steps: int
    """Relative steps: positive = right/clockwise, negative = left/counter-clockwise."""
    shifted: bool
    """``True`` when the SHIFT key was held during the turn."""

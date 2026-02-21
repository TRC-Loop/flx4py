"""
Main DDJ-FLX4 controller class.
"""

import threading
import traceback
from collections import defaultdict
from typing import Callable

import mido

from .events import (
    BrowseEvent,
    ButtonEvent,
    JogEvent,
    JogTouchEvent,
    KnobEvent,
    PadEvent,
    TabEvent,
)
from .leds import LEDController
from .mappings import (
    BROWSE_INPUT,
    BUTTON_INPUT,
    JOG_INPUT,
    JOG_TOUCH_INPUT,
    KNOB_14BIT_INPUT,
    KNOB_14BIT_LSB,
    KNOB_7BIT_INPUT,
    PAD_INPUT,
    TAB_INPUT,
)


def _find_port(names: list[str], keyword: str) -> str | None:
    for name in names:
        if keyword in name:
            return name
    return None


class DDJFlx4:
    """
    High-level interface to the Pioneer DDJ-FLX4.

    Opens both the MIDI input (to receive knob/button/pad events) and the
    MIDI output (to drive LEDs) automatically on instantiation.

    Args:
        keyword: Substring used to locate the controller's MIDI ports.
                 Defaults to ``'FLX4'``.

    Raises:
        RuntimeError: If no matching input or output port is found.

    Example::

        import flx4py

        controller = flx4py.DDJFlx4()

        @controller.on_pad(deck=1)
        def pad_pressed(event: flx4py.PadEvent):
            if event.pressed:
                controller.leds.set_pad(event.deck, event.pad, True)

        controller.start()
    """

    def __init__(self, keyword: str = 'FLX4') -> None:
        in_name = _find_port(mido.get_input_names(), keyword)
        out_name = _find_port(mido.get_output_names(), keyword)

        if in_name is None:
            raise RuntimeError(
                f"No MIDI input port matching '{keyword}' found. "
                f"Available: {mido.get_input_names()}"
            )
        if out_name is None:
            raise RuntimeError(
                f"No MIDI output port matching '{keyword}' found. "
                f"Available: {mido.get_output_names()}"
            )

        self._input = mido.open_input(in_name)
        self._output = mido.open_output(out_name)

        self.leds = LEDController(self._output)
        """LED controller. Use this to set pads, buttons, and VU meters."""

        self._callbacks: dict[str, list[tuple[Callable, dict]]] = defaultdict(list)
        self._lock = threading.Lock()
        self._control_state: dict[str, dict] = {}  # 14-bit MSB/LSB buffers
        self._values: dict[tuple[str, int | None], float] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the background MIDI listener thread.

        After calling this, registered callbacks will fire whenever the
        controller sends a message. Safe to call only once.
        """
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name='flx4py-listener')
        self._thread.start()

    def stop(self) -> None:
        """
        Stop the background listener thread and close MIDI ports.

        The :class:`LEDController` is unusable after calling this.
        """
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._input.close()
        self._output.close()

    def __enter__(self) -> 'DDJFlx4':
        self.start()
        return self

    def __exit__(self, *_) -> None:
        self.stop()

    # ------------------------------------------------------------------
    # Current-value queries
    # ------------------------------------------------------------------

    def get_value(self, name: str, deck: int | None = None) -> float | None:
        """
        Return the last known normalised value of a knob or fader.

        Values are populated as messages arrive; returns ``None`` if the
        control has not moved since the controller was opened.

        Args:
            name: Control name, e.g. ``'CH_FADER'``, ``'CROSSFADER'``, ``'TEMPO'``.
            deck: Deck number for deck-specific controls; ``None`` for globals.

        Returns:
            A ``float`` in ``0.0–1.0`` (or ``-1.0–1.0`` for ``TEMPO``),
            or ``None`` if no value has been received yet.
        """
        return self._values.get((name, deck))

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def _register(self, event_type: str, func: Callable, filters: dict) -> None:
        with self._lock:
            self._callbacks[event_type].append((func, {k: v for k, v in filters.items() if v is not None}))

    def _make_decorator(self, event_type: str, filters: dict, callback: Callable | None):
        def decorator(func: Callable) -> Callable:
            self._register(event_type, func, filters)
            return func
        if callback is not None:
            decorator(callback)
            return None
        return decorator

    def on_pad(
        self,
        deck: int | None = None,
        pressed: bool | None = None,
        *,
        callback: Callable | None = None,
    ):
        """
        Register a callback for performance pad events.

        Can be used as a decorator or called directly with ``callback=``.

        Args:
            deck: Filter to deck 1 or 2; ``None`` matches both.
            pressed: Filter to press (``True``) or release (``False``) only.
            callback: Function to register directly instead of using as a decorator.

        Example::

            @controller.on_pad(deck=1, pressed=True)
            def handler(event: PadEvent):
                controller.leds.set_pad(event.deck, event.pad, True)
        """
        return self._make_decorator('pad', {'deck': deck, 'pressed': pressed}, callback)

    def on_tab(
        self,
        deck: int | None = None,
        pressed: bool | None = None,
        *,
        callback: Callable | None = None,
    ):
        """
        Register a callback for tab key (HOT CUE / PAD FX / BEAT JUMP / SAMPLER) events.

        Args:
            deck: Filter to deck 1 or 2.
            pressed: Filter to press or release only.
            callback: Register directly instead of using as decorator.
        """
        return self._make_decorator('tab', {'deck': deck, 'pressed': pressed}, callback)

    def on_button(
        self,
        name: str | None = None,
        deck: int | None = None,
        shifted: bool | None = None,
        pressed: bool | None = None,
        *,
        callback: Callable | None = None,
    ):
        """
        Register a callback for named button events.

        Args:
            name: Button name to filter on, e.g. ``'PLAY_PAUSE'``, ``'CUE'``,
                  ``'BEAT_SYNC'``, ``'MASTER_CUE'``, ``'BROWSE_PRESS'``.
                  ``None`` matches all buttons.
            deck: Filter to a specific deck; ``None`` matches all.
            shifted: Filter to shifted or unshifted state.
            pressed: Filter to press or release only.
            callback: Register directly instead of using as decorator.

        Example::

            @controller.on_button('PLAY_PAUSE', deck=1, pressed=True)
            def play(event: ButtonEvent):
                print("Play pressed on deck 1")
        """
        return self._make_decorator(
            'button',
            {'name': name, 'deck': deck, 'shifted': shifted, 'pressed': pressed},
            callback,
        )

    def on_knob(
        self,
        name: str | None = None,
        deck: int | None = None,
        *,
        callback: Callable | None = None,
    ):
        """
        Register a callback for absolute knob/fader events.

        This covers channel faders, EQ knobs, trim, CFX, crossfader, master
        level, headphone controls, mic level, smart fader, and the
        mono/stereo slider.

        Args:
            name: Control name to filter on, e.g. ``'CH_FADER'``,
                  ``'CROSSFADER'``, ``'EQ_HI'``. ``None`` matches all.
            deck: Filter to a specific deck; ``None`` matches all.
            callback: Register directly instead of using as decorator.

        Example::

            @controller.on_knob('CROSSFADER')
            def crossfader(event: KnobEvent):
                print(f"Crossfader: {event.value:.2f}")
        """
        return self._make_decorator('knob', {'name': name, 'deck': deck}, callback)

    def on_jog(
        self,
        deck: int | None = None,
        surface: str | None = None,
        *,
        callback: Callable | None = None,
    ):
        """
        Register a callback for jog wheel rotation events.

        Args:
            deck: Filter to deck 1 or 2.
            surface: Filter to ``'top'`` (platter) or ``'side'`` (outer ring).
            callback: Register directly instead of using as decorator.

        Example::

            @controller.on_jog(deck=1, surface='top')
            def jog_top(event: JogEvent):
                print(f"Jog deck 1 top: {event.direction:+d}")
        """
        return self._make_decorator('jog', {'deck': deck, 'surface': surface}, callback)

    def on_jog_touch(
        self,
        deck: int | None = None,
        *,
        callback: Callable | None = None,
    ):
        """
        Register a callback for jog wheel touch/release events.

        Args:
            deck: Filter to deck 1 or 2.
            callback: Register directly instead of using as decorator.
        """
        return self._make_decorator('jog_touch', {'deck': deck}, callback)

    def on_browse(
        self,
        shifted: bool | None = None,
        *,
        callback: Callable | None = None,
    ):
        """
        Register a callback for browse encoder rotation events.

        Args:
            shifted: Filter to shifted or unshifted turns.
            callback: Register directly instead of using as decorator.

        Example::

            @controller.on_browse()
            def browse(event: BrowseEvent):
                print(f"Browse: {event.steps:+d} steps")
        """
        return self._make_decorator('browse', {'shifted': shifted}, callback)

    def on_any(self, callback: Callable) -> Callable:
        """
        Register a callback that fires for every event regardless of type.

        The callback receives a single positional argument which may be any
        event dataclass.

        Args:
            callback: Callable accepting one event argument.

        Returns:
            The callback unchanged (so it can be used as a decorator).
        """
        with self._lock:
            self._callbacks['any'].append((callback, {}))
        return callback

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, event_type: str, event) -> None:
        with self._lock:
            typed = list(self._callbacks[event_type])
            any_cbs = list(self._callbacks['any'])

        for func, filters in typed:
            if all(getattr(event, k, None) == v for k, v in filters.items()):
                try:
                    func(event)
                except Exception:
                    traceback.print_exc()

        for func, _ in any_cbs:
            try:
                func(event)
            except Exception:
                traceback.print_exc()

    # ------------------------------------------------------------------
    # MIDI listener
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        while self._running:
            for msg in self._input.iter_pending():
                try:
                    self._handle(msg)
                except Exception:
                    traceback.print_exc()
            threading.Event().wait(0.001)  # 1 ms poll

    def _handle(self, msg: mido.Message) -> None:
        if msg.type == 'note_on':
            self._handle_note(msg)
        elif msg.type == 'control_change':
            self._handle_cc(msg)

    def _handle_note(self, msg: mido.Message) -> None:
        pressed = msg.velocity > 0
        key = (msg.channel, msg.note)

        if key in PAD_INPUT:
            deck, pad = PAD_INPUT[key]
            self._dispatch('pad', PadEvent(deck=deck, pad=pad, pressed=pressed, velocity=msg.velocity))

        elif key in TAB_INPUT:
            deck, tab = TAB_INPUT[key]
            self._dispatch('tab', TabEvent(deck=deck, tab=tab, pressed=pressed))

        elif key in JOG_TOUCH_INPUT:
            deck = JOG_TOUCH_INPUT[key]
            self._dispatch('jog_touch', JogTouchEvent(deck=deck, touched=pressed))

        elif key in BUTTON_INPUT:
            info = BUTTON_INPUT[key]
            self._dispatch('button', ButtonEvent(
                name=info.name, deck=info.deck, shifted=info.shifted, pressed=pressed,
            ))

    def _handle_cc(self, msg: mido.Message) -> None:
        key = (msg.channel, msg.control)

        if key in JOG_INPUT:
            info = JOG_INPUT[key]
            raw = msg.value
            direction = +1 if raw > 64 else -1
            velocity = abs(raw - 64)
            self._dispatch('jog', JogEvent(deck=info.deck, surface=info.surface, direction=direction, velocity=velocity))

        elif key in BROWSE_INPUT:
            shifted = BROWSE_INPUT[key]
            raw = msg.value
            if 1 <= raw <= 64:
                steps = raw
            else:
                steps = -(128 - raw)
            self._dispatch('browse', BrowseEvent(steps=steps, shifted=shifted))

        elif key in KNOB_14BIT_INPUT:
            # MSB of a 14-bit control
            info = KNOB_14BIT_INPUT[key]
            state_key = f"{msg.channel}_{info.name}"
            if state_key not in self._control_state:
                self._control_state[state_key] = {'msb': 0, 'lsb': 0, 'info': info}
            self._control_state[state_key]['msb'] = msg.value

        elif key in KNOB_14BIT_LSB:
            # LSB of a 14-bit control — fire event on LSB (complete pair)
            msb_key = KNOB_14BIT_LSB[key]
            info = KNOB_14BIT_INPUT[msb_key]
            state_key = f"{msg.channel}_{info.name}"
            if state_key not in self._control_state:
                self._control_state[state_key] = {'msb': 0, 'lsb': 0, 'info': info}
            self._control_state[state_key]['lsb'] = msg.value

            msb = self._control_state[state_key]['msb']
            lsb = self._control_state[state_key]['lsb']
            raw = (msb << 7) | lsb

            if info.name == 'TEMPO':
                value = max(-1.0, min(1.0, (raw - 8192) / 8192.0))
            else:
                value = raw / 16383.0

            self._values[(info.name, info.deck)] = value
            self._dispatch('knob', KnobEvent(name=info.name, deck=info.deck, value=value, raw=raw))

        elif key in KNOB_7BIT_INPUT:
            info = KNOB_7BIT_INPUT[key]
            value = msg.value / 127.0
            self._values[(info.name, info.deck)] = value
            self._dispatch('knob', KnobEvent(name=info.name, deck=info.deck, value=value, raw=msg.value))

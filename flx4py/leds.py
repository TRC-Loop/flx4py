"""
LED control for the Pioneer DDJ-FLX4.

The ``LEDController`` class provides methods to set individual LEDs and run
built-in animations on the pads, buttons, and VU meters.
"""

import time
from enum import Enum

import mido

from .mappings import (
    BUTTON_LED,
    LEVEL_METER_CC,
    PAD_LED_CHANNELS,
    PAD_LED_MODES,
)


class LEDState(Enum):
    """Binary LED state."""
    OFF = 0x00
    ON = 0x7F


class PadMode(str, Enum):
    """Performance pad LED modes."""
    HOT_CUE   = 'HOT_CUE'
    PAD_FX_1  = 'PAD_FX_1'
    PAD_FX_2  = 'PAD_FX_2'
    BEAT_JUMP = 'BEAT_JUMP'
    SAMPLER   = 'SAMPLER'
    KEYBOARD  = 'KEYBOARD'
    BEAT_LOOP = 'BEAT_LOOP'
    KEY_SHIFT = 'KEY_SHIFT'


class LEDController:
    """
    Controls all LEDs on the DDJ-FLX4 over MIDI.

    Typically accessed via :attr:`DDJFlx4.leds` rather than instantiated
    directly.

    Args:
        output: An open ``mido`` output port connected to the controller.
    """

    def __init__(self, output: mido.ports.BaseOutput) -> None:
        self._out = output

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _note(self, channel: int, note: int, velocity: int) -> None:
        self._out.send(mido.Message('note_on', channel=channel, note=note, velocity=velocity))

    def _cc(self, channel: int, control: int, value: int) -> None:
        self._out.send(mido.Message('control_change', channel=channel, control=control, value=value))

    # ------------------------------------------------------------------
    # Performance pads
    # ------------------------------------------------------------------

    def set_pad(
        self,
        deck: int,
        pad: int,
        on: bool,
        mode: str | PadMode = PadMode.HOT_CUE,
        shifted: bool = False,
    ) -> None:
        """
        Set a single performance pad LED.

        Args:
            deck: 1 or 2.
            pad: Pad index 0–7.
            on: ``True`` to light the pad, ``False`` to turn it off.
            mode: Pad mode string or :class:`PadMode` value.
            shifted: Use the shifted pad channel.

        Raises:
            ValueError: If *deck*, *pad*, or *mode* is invalid.
        """
        if deck not in (1, 2):
            raise ValueError("deck must be 1 or 2")
        if not 0 <= pad <= 7:
            raise ValueError("pad must be 0–7")
        mode_str = PadMode(mode).value if isinstance(mode, str) else mode.value
        if mode_str not in PAD_LED_MODES:
            raise ValueError(f"unknown mode '{mode_str}'")

        normal_ch, shifted_ch = PAD_LED_CHANNELS[deck]
        channel = shifted_ch if shifted else normal_ch
        note = PAD_LED_MODES[mode_str] + pad
        self._note(channel, note, LEDState.ON.value if on else LEDState.OFF.value)

    def set_all_pads(
        self,
        deck: int,
        on: bool,
        mode: str | PadMode = PadMode.HOT_CUE,
        shifted: bool = False,
    ) -> None:
        """Set all 8 pads on *deck* to the same state."""
        for i in range(8):
            self.set_pad(deck, i, on, mode, shifted)

    def clear_pads(self, deck: int, mode: str | PadMode = PadMode.HOT_CUE) -> None:
        """Turn off all pads on *deck* in *mode* (both normal and shifted)."""
        self.set_all_pads(deck, False, mode, shifted=False)
        self.set_all_pads(deck, False, mode, shifted=True)

    # ------------------------------------------------------------------
    # Deck buttons
    # ------------------------------------------------------------------

    def set_button(
        self,
        name: str,
        on: bool,
        deck: int | None = None,
        shifted: bool = False,
    ) -> None:
        """
        Set a named button LED.

        Args:
            name: Button name, e.g. ``'PLAY_PAUSE'``, ``'CUE'``, ``'BEAT_SYNC'``.
            on: ``True`` to light the button, ``False`` to turn it off.
            deck: 1 or 2 for deck buttons; ``None`` for global buttons
                  (FX, mixer, browse).
            shifted: Address the shifted variant of the button.

        Raises:
            ValueError: If the button name / deck combination is not found.
        """
        key = (name, deck, shifted)
        if key not in BUTTON_LED:
            raise ValueError(f"unknown button '{name}' with deck={deck}, shifted={shifted}")
        channel, note = BUTTON_LED[key]
        self._note(channel, note, LEDState.ON.value if on else LEDState.OFF.value)

    def set_tab(self, deck: int, tab: int, on: bool) -> None:
        """
        Set a pad-mode tab button LED.

        Args:
            deck: 1 or 2.
            tab: Tab index 0–3 (HOT CUE, PAD FX, BEAT JUMP, SAMPLER).
            on: ``True`` to light, ``False`` to turn off.
        """
        tab_notes = {0: 27, 1: 30, 2: 32, 3: 34}
        if tab not in tab_notes:
            raise ValueError("tab must be 0–3")
        channel = 0 if deck == 1 else 1
        self._note(channel, tab_notes[tab], LEDState.ON.value if on else LEDState.OFF.value)

    # ------------------------------------------------------------------
    # VU level meters
    # ------------------------------------------------------------------

    def set_level_meter(self, deck: int, level: float) -> None:
        """
        Set the channel VU meter using a normalised value.

        Args:
            deck: 1 or 2.
            level: 0.0 (off) to 1.0 (peak / red). Values are mapped to the
                   controller's green → orange → red LED segments automatically.

        Raises:
            ValueError: If *deck* or *level* is out of range.
        """
        if deck not in (1, 2):
            raise ValueError("deck must be 1 or 2")
        if not 0.0 <= level <= 1.0:
            raise ValueError("level must be 0.0–1.0")
        channel = 0 if deck == 1 else 1
        self._cc(channel, LEVEL_METER_CC, int(level * 127))

    def set_level_meter_raw(self, deck: int, value: int) -> None:
        """
        Set the channel VU meter using a raw MIDI value.

        Args:
            deck: 1 or 2.
            value: 0–127.
        """
        if deck not in (1, 2):
            raise ValueError("deck must be 1 or 2")
        if not 0 <= value <= 127:
            raise ValueError("value must be 0–127")
        channel = 0 if deck == 1 else 1
        self._cc(channel, LEVEL_METER_CC, value)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def all_off(self) -> None:
        """Turn off every controllable LED on the controller."""
        for deck in (1, 2):
            self.set_level_meter(deck, 0.0)
            for mode in PAD_LED_MODES:
                self.clear_pads(deck, mode)
            for tab in range(4):
                self.set_tab(deck, tab, False)

        for (name, deck, shifted), _ in BUTTON_LED.items():
            try:
                self.set_button(name, False, deck, shifted)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Built-in animations
    # ------------------------------------------------------------------

    def animate_wave(self, duration: float = 10.0, speed: float = 0.06) -> None:
        """
        A single lit pad sweeps across both decks in sync.

        Args:
            duration: Seconds to run.
            speed: Seconds between steps.
        """
        end = time.monotonic() + duration
        pos = 0
        while time.monotonic() < end:
            for deck in (1, 2):
                for i in range(8):
                    self.set_pad(deck, i, i == pos % 8)
            pos += 1
            time.sleep(speed)
        self.all_off()

    def animate_knight_rider(self, duration: float = 10.0, speed: float = 0.05) -> None:
        """
        A single lit pad bounces left–right on both decks while the VU meters follow.

        Args:
            duration: Seconds to run.
            speed: Seconds between steps.
        """
        end = time.monotonic() + duration
        while time.monotonic() < end:
            for i in range(8):
                if time.monotonic() >= end:
                    break
                for deck in (1, 2):
                    for j in range(8):
                        self.set_pad(deck, j, j == i)
                level = i / 7
                self.set_level_meter(1, level)
                self.set_level_meter(2, level)
                time.sleep(speed)
            for i in range(6, 0, -1):
                if time.monotonic() >= end:
                    break
                for deck in (1, 2):
                    for j in range(8):
                        self.set_pad(deck, j, j == i)
                level = i / 7
                self.set_level_meter(1, level)
                self.set_level_meter(2, level)
                time.sleep(speed)
        self.all_off()

    def animate_breathing(self, duration: float = 10.0, cycle: float = 2.0) -> None:
        """
        Pads and VU meters pulse in and out together like breathing.

        Args:
            duration: Seconds to run.
            cycle: Duration of one full breath cycle in seconds.
        """
        end = time.monotonic() + duration
        steps = 40
        delay = cycle / (steps * 2)
        while time.monotonic() < end:
            for phase in range(steps * 2):
                if time.monotonic() >= end:
                    break
                t = phase / steps
                level = t if t <= 1.0 else 2.0 - t
                num_pads = int(level * 8)
                self.set_level_meter(1, level)
                self.set_level_meter(2, level)
                for deck in (1, 2):
                    for p in range(8):
                        self.set_pad(deck, p, p < num_pads)
                time.sleep(delay)
        self.all_off()

    def animate_ping_pong(self, duration: float = 10.0, speed: float = 0.05) -> None:
        """
        A lit pad travels from deck 1 through to deck 2 and back.

        Args:
            duration: Seconds to run.
            speed: Seconds between steps.
        """
        end = time.monotonic() + duration
        while time.monotonic() < end:
            for i in range(8):
                if time.monotonic() >= end:
                    break
                for j in range(8):
                    self.set_pad(1, j, j == i)
                self.set_level_meter(1, i / 7)
                time.sleep(speed)
            for i in range(8):
                if time.monotonic() >= end:
                    break
                for j in range(8):
                    self.set_pad(1, j, False)
                    self.set_pad(2, j, j == i)
                self.set_level_meter(1, 1.0 - i / 7)
                self.set_level_meter(2, i / 7)
                time.sleep(speed)
            for i in range(7, -1, -1):
                if time.monotonic() >= end:
                    break
                for j in range(8):
                    self.set_pad(2, j, j == i)
                self.set_level_meter(2, i / 7)
                time.sleep(speed)
            self.set_level_meter(1, 0.0)
            self.set_level_meter(2, 0.0)
        self.all_off()

    def animate_sparkle(self, duration: float = 10.0, speed: float = 0.08) -> None:
        """
        Random pads and buttons twinkle on and off.

        Args:
            duration: Seconds to run.
            speed: Seconds between each change.
        """
        import random
        end = time.monotonic() + duration
        active: list[tuple] = []

        deck_buttons = [
            ('PLAY_PAUSE', 1), ('PLAY_PAUSE', 2),
            ('CUE', 1), ('CUE', 2),
            ('BEAT_SYNC', 1), ('BEAT_SYNC', 2),
        ]

        while time.monotonic() < end:
            deck = random.choice((1, 2))
            pad = random.randint(0, 7)
            self.set_pad(deck, pad, True)
            active.append(('pad', deck, pad))

            if random.random() > 0.65:
                btn, btn_deck = random.choice(deck_buttons)
                try:
                    self.set_button(btn, True, btn_deck)
                    active.append(('btn', btn_deck, btn))
                except Exception:
                    pass

            while len(active) > 10:
                item = active.pop(0)
                if item[0] == 'pad':
                    self.set_pad(item[1], item[2], False)
                else:
                    try:
                        self.set_button(item[2], False, item[1])
                    except Exception:
                        pass

            time.sleep(speed)

        for item in active:
            if item[0] == 'pad':
                self.set_pad(item[1], item[2], False)
            else:
                try:
                    self.set_button(item[2], False, item[1])
                except Exception:
                    pass

    def animate_rainbow_chase(self, duration: float = 10.0, speed: float = 0.08) -> None:
        """
        A moving group of lit pads chases across both decks with opposing VU meters.

        Args:
            duration: Seconds to run.
            speed: Seconds between steps.
        """
        end = time.monotonic() + duration
        offset = 0
        while time.monotonic() < end:
            for deck in (1, 2):
                for i in range(8):
                    pos = (i + offset + (deck - 1) * 4) % 16
                    self.set_pad(deck, i, pos < 4)
            meter = abs(8 - (offset % 16)) / 8
            self.set_level_meter(1, meter)
            self.set_level_meter(2, 1.0 - meter)
            offset += 1
            time.sleep(speed)
        self.all_off()

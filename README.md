# flx4py

Python library for the Pioneer DDJ-FLX4 DJ controller.

Full programmatic access to every button, knob, fader, jog wheel, and LED on the device — with a clean, callback-based API.

```python
import flx4py

controller = flx4py.DDJFlx4()

@controller.on_pad(deck=1, pressed=True)
def pad_pressed(event: flx4py.PadEvent):
    controller.leds.set_pad(event.deck, event.pad, True)

@controller.on_knob("CROSSFADER")
def crossfader(event: flx4py.KnobEvent):
    controller.leds.set_level_meter(1, event.value)
    controller.leds.set_level_meter(2, 1.0 - event.value)

with controller:
    import time
    while True:
        time.sleep(1)
```

## Install

```bash
pip install flx4py
```

Requires Python 3.10+ and a DDJ-FLX4 connected over USB.

## Features

- **Callbacks** for pads, buttons, knobs, faders, jog wheels, and the browse encoder
- **LED control** for pads (all modes), transport buttons, tab keys, FX buttons, and VU meters
- **Built-in animations** — wave, knight rider, breathing, sparkle, ping pong, rainbow chase
- **Current value queries** — ask for the last known position of any knob or fader
- 14-bit resolution for faders and knobs
- Context manager for clean resource management

## Documentation

Full docs at **[trc-loop.github.io/flx4py](https://trc-loop.github.io/flx4py/)**

## Quick reference

```python
# Pads
@controller.on_pad(deck=1, pressed=True)
def handler(event: flx4py.PadEvent): ...

# Buttons
@controller.on_button("PLAY_PAUSE", deck=1, pressed=True)
def handler(event: flx4py.ButtonEvent): ...

# Knobs / faders
@controller.on_knob("CH_FADER", deck=1)
def handler(event: flx4py.KnobEvent): ...  # event.value = 0.0–1.0

# Jog wheels
@controller.on_jog(deck=1, surface="top")
def handler(event: flx4py.JogEvent): ...  # event.direction = +1 or -1

# Browse encoder
@controller.on_browse()
def handler(event: flx4py.BrowseEvent): ...  # event.steps = ±n

# LEDs
controller.leds.set_pad(deck=1, pad=0, on=True)
controller.leds.set_button("PLAY_PAUSE", on=True, deck=1)
controller.leds.set_level_meter(deck=1, level=0.75)
controller.leds.all_off()

# Query current values
fader = controller.get_value("CH_FADER", deck=1)    # 0.0–1.0
tempo = controller.get_value("TEMPO", deck=1)        # -1.0–1.0
cross = controller.get_value("CROSSFADER")           # 0.0–1.0
```

## License

MIT

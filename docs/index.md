# flx4py

**flx4py** is a Python library for the Pioneer DDJ-FLX4 DJ controller. It gives you full programmatic access to every button, knob, fader, jog wheel, and LED on the device using a clean, callback-based API.

```python
import flx4py

controller = flx4py.DDJFlx4()

@controller.on_pad(deck=1, pressed=True)
def pad_pressed(event: flx4py.PadEvent):
    controller.leds.set_pad(event.deck, event.pad, True)
    print(f"Pad {event.pad} pressed on deck {event.deck}")

@controller.on_knob("CROSSFADER")
def crossfader(event: flx4py.KnobEvent):
    print(f"Crossfader: {event.value:.2f}")

with controller:
    import time
    while True:
        time.sleep(1)
```

## What you can do

- **Read every control** — pads, buttons, knobs, faders, jog wheels, browse encoder, and more, all with normalised floating-point values.
- **Control every LED** — pads (all modes), transport buttons, tab keys, FX buttons, browse buttons, and the VU meters on both decks.
- **Register callbacks** with fine-grained filters — per deck, per button name, press vs release, shifted vs unshifted.
- **Run animations** — built-in LED animations for screensavers or visual feedback.

## Requirements

- Python 3.10+
- Pioneer DDJ-FLX4 connected over USB
- The controller must appear as a MIDI device (no additional drivers needed on most systems)

## Useful reference

The full MIDI message specification from Pioneer DJ:
**[DDJ-FLX4 MIDI Message List (PDF)](https://www.pioneerdj.com/-/media/pioneerdj/software-info/controller/ddj-flx4/ddj-flx4_midi_message_list_e1.pdf)**

Note that some values in the official document don't match what the device actually sends — see [MIDI Mappings](mappings.md) for the corrected table.

## Install

```bash
pip install flx4py
```

See [Installation](guide/installation.md) for details.

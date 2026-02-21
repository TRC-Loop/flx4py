# Quick Start

This page walks you through the basics of using flx4py.

## 1. Connect the controller

```python
import flx4py

controller = flx4py.DDJFlx4()
```

`DDJFlx4()` scans all MIDI ports, opens the first one whose name contains `'FLX4'`, and returns a connected controller object. It raises `RuntimeError` if the device is not found.

You can pass a custom keyword if needed:

```python
controller = flx4py.DDJFlx4(keyword="DDJ")
```

## 2. Register callbacks

Callbacks fire whenever the corresponding control is used. Register them with the `on_*` methods, which work as decorators:

```python
@controller.on_pad(deck=1, pressed=True)
def pad_pressed(event: flx4py.PadEvent):
    print(f"Pad {event.pad} pressed on deck {event.deck}")

@controller.on_button("PLAY_PAUSE", deck=1)
def play_pause(event: flx4py.ButtonEvent):
    state = "pressed" if event.pressed else "released"
    print(f"Play/Pause {state} on deck 1")

@controller.on_knob("CROSSFADER")
def crossfader(event: flx4py.KnobEvent):
    print(f"Crossfader: {event.value:.2f}")
```

See [Callbacks](callbacks.md) for the full list of callback types and their filter options.

## 3. Start listening

```python
controller.start()
```

This launches a background thread. Your main thread is free to do other work:

```python
controller.start()
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    controller.stop()
```

## 4. Use the context manager

The cleanest pattern is the context manager, which calls `start()` on entry and `stop()` (including closing MIDI ports) on exit:

```python
with flx4py.DDJFlx4() as controller:

    @controller.on_pad()
    def any_pad(event: flx4py.PadEvent):
        print(event)

    import time
    while True:
        time.sleep(1)
```

## 5. Control LEDs

Access the LED controller through `controller.leds`:

```python
# Light pad 0 on deck 1
controller.leds.set_pad(deck=1, pad=0, on=True)

# Turn it off
controller.leds.set_pad(deck=1, pad=0, on=False)

# Set VU meter to 75%
controller.leds.set_level_meter(deck=1, level=0.75)

# Light the Play/Pause button on deck 2
controller.leds.set_button("PLAY_PAUSE", on=True, deck=2)

# Turn everything off
controller.leds.all_off()
```

See [LED Control](leds.md) for the full LED API.

## 6. Query current values

You can read the last known value of any knob or fader at any time:

```python
fader = controller.get_value("CH_FADER", deck=1)  # 0.0–1.0
crossfader = controller.get_value("CROSSFADER")    # 0.0–1.0
tempo = controller.get_value("TEMPO", deck=1)      # -1.0–1.0
```

Returns `None` if the control hasn't been moved since the controller was opened.

## Complete example

```python
import time
import flx4py

controller = flx4py.DDJFlx4()

@controller.on_pad(deck=1, pressed=True)
def pad_on(event: flx4py.PadEvent):
    controller.leds.set_pad(event.deck, event.pad, True)

@controller.on_pad(deck=1, pressed=False)
def pad_off(event: flx4py.PadEvent):
    controller.leds.set_pad(event.deck, event.pad, False)

@controller.on_knob("CROSSFADER")
def crossfader_moved(event: flx4py.KnobEvent):
    # Mirror crossfader position on both VU meters
    controller.leds.set_level_meter(1, event.value)
    controller.leds.set_level_meter(2, 1.0 - event.value)

with controller:
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        controller.leds.all_off()
```

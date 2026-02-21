# LED Control

The `LEDController` is available as `controller.leds` and lets you control every LED on the DDJ-FLX4.

## Performance pads

Each deck has 8 performance pads. Pads can be set in any of the available modes.

```python
# Light pad 3 on deck 1 (HOT CUE mode by default)
controller.leds.set_pad(deck=1, pad=3, on=True)

# Turn it off
controller.leds.set_pad(deck=1, pad=3, on=False)

# Light pad 0 on deck 2 in BEAT JUMP mode
controller.leds.set_pad(deck=2, pad=0, on=True, mode="BEAT_JUMP")

# Light all pads on deck 1
controller.leds.set_all_pads(deck=1, on=True)

# Clear all pads on deck 2 (both normal and shifted layers)
controller.leds.clear_pads(deck=2)
```

### Pad modes

| Mode string | Physical mode |
|-------------|--------------|
| `'HOT_CUE'` | Hot Cue |
| `'PAD_FX_1'` | Pad FX 1 |
| `'PAD_FX_2'` | Pad FX 2 |
| `'BEAT_JUMP'` | Beat Jump |
| `'SAMPLER'` | Sampler |
| `'KEYBOARD'` | Keyboard |
| `'BEAT_LOOP'` | Beat Loop |
| `'KEY_SHIFT'` | Key Shift |

You can also use the `PadMode` enum:

```python
from flx4py import PadMode
controller.leds.set_pad(deck=1, pad=0, on=True, mode=PadMode.SAMPLER)
```

## Buttons

```python
# Deck buttons
controller.leds.set_button("PLAY_PAUSE", on=True, deck=1)
controller.leds.set_button("CUE", on=False, deck=2)
controller.leds.set_button("BEAT_SYNC", on=True, deck=1)

# Shifted variant of a button
controller.leds.set_button("PLAY_PAUSE", on=True, deck=1, shifted=True)

# FX buttons (no deck)
controller.leds.set_button("FX_ON_OFF", on=True)
controller.leds.set_button("FX_BEAT_LEFT", on=False)

# FX channel-select (has a deck)
controller.leds.set_button("FX_CH_SELECT", on=True, deck=1)

# Mixer
controller.leds.set_button("MASTER_CUE", on=True)

# Browse
controller.leds.set_button("BROWSE_LOAD", on=True, deck=1)
controller.leds.set_button("BROWSE_PRESS", on=False)
```

## Tab keys

```python
controller.leds.set_tab(deck=1, tab=0, on=True)   # HOT CUE tab
controller.leds.set_tab(deck=1, tab=1, on=False)  # PAD FX tab
```

Tab indices: `0` = HOT CUE, `1` = PAD FX, `2` = BEAT JUMP, `3` = SAMPLER.

## VU meters

The VU meters accept a normalised value from `0.0` (off) to `1.0` (red/peak):

```python
controller.leds.set_level_meter(deck=1, level=0.0)    # Off
controller.leds.set_level_meter(deck=1, level=0.5)    # Half (orange)
controller.leds.set_level_meter(deck=2, level=1.0)    # Full (red)
```

If you need raw MIDI values (0–127):

```python
controller.leds.set_level_meter_raw(deck=1, value=64)
```

## Turn everything off

```python
controller.leds.all_off()
```

This turns off every pad, button, tab, and VU meter on both decks.

## Practical pattern: mirror pad presses with LEDs

```python
@controller.on_pad(deck=1, pressed=True)
def pad_on(event):
    controller.leds.set_pad(event.deck, event.pad, True)

@controller.on_pad(deck=1, pressed=False)
def pad_off(event):
    controller.leds.set_pad(event.deck, event.pad, False)
```

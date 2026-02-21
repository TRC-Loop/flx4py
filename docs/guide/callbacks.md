# Callbacks

flx4py uses a callback system: you register functions that are called whenever a specific event occurs. Callbacks fire in a background thread, so keep them fast — offload heavy work to a queue if needed.

## Registering callbacks

Every `on_*` method works as a **decorator**:

```python
@controller.on_pad(deck=1)
def handler(event: flx4py.PadEvent):
    ...
```

Or you can register a function directly using the `callback=` keyword:

```python
def handler(event: flx4py.PadEvent):
    ...

controller.on_pad(deck=1, callback=handler)
```

All filter parameters are optional — omit them to match everything.

---

## on_pad — Performance pads

```python
@controller.on_pad(deck=None, pressed=None)
def handler(event: flx4py.PadEvent): ...
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `deck` | `int \| None` | Filter to deck 1 or 2; `None` = both |
| `pressed` | `bool \| None` | `True` = press only, `False` = release only |

**Event fields:**

| Field | Type | Description |
|-------|------|-------------|
| `deck` | `int` | 1 or 2 |
| `pad` | `int` | 0–7 (left to right) |
| `pressed` | `bool` | `True` on press, `False` on release |
| `velocity` | `int` | Raw MIDI velocity 0–127 |

```python
@controller.on_pad(deck=1, pressed=True)
def pad_pressed(event: flx4py.PadEvent):
    controller.leds.set_pad(event.deck, event.pad, True)
```

---

## on_tab — Tab keys

The four tab keys above each deck switch the pad mode (HOT CUE / PAD FX / BEAT JUMP / SAMPLER).

```python
@controller.on_tab(deck=None, pressed=None)
def handler(event: flx4py.TabEvent): ...
```

**Event fields:**

| Field | Type | Description |
|-------|------|-------------|
| `deck` | `int` | 1 or 2 |
| `tab` | `int` | 0 = HOT CUE, 1 = PAD FX, 2 = BEAT JUMP, 3 = SAMPLER |
| `pressed` | `bool` | `True` on press |

---

## on_button — Named buttons

```python
@controller.on_button(name=None, deck=None, shifted=None, pressed=None)
def handler(event: flx4py.ButtonEvent): ...
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str \| None` | Button name (see table below) |
| `deck` | `int \| None` | 1 or 2 for deck buttons; `None` for global buttons |
| `shifted` | `bool \| None` | Filter shifted vs unshifted |
| `pressed` | `bool \| None` | Filter press vs release |

**Deck buttons** (use `deck=1` or `deck=2`):

| Name | Physical button |
|------|----------------|
| `PLAY_PAUSE` | Play/Pause |
| `CUE` | Cue |
| `CUE_LOOP_CALL` | Cue/Loop Call |
| `IN` | In (loop in) |
| `OUT` | Out (loop out) |
| `BEAT_4_EXIT` | 4 Beat / Exit |
| `CUE_LOOP_LEFT` | Cue/Loop ◄ |
| `CUE_LOOP_RIGHT` | Cue/Loop ► |
| `BEAT_SYNC` | Beat Sync |
| `BEAT_SYNC_LONG` | Beat Sync (long press) |
| `SHIFT` | Shift |

**FX buttons** (use `deck=None` unless noted):

| Name | `deck` | Physical button |
|------|--------|----------------|
| `FX_BEAT_LEFT` | `None` | FX Beat ◄ |
| `FX_BEAT_RIGHT` | `None` | FX Beat ► |
| `FX_ON_OFF` | `None` | FX On/Off |
| `FX_CH_SELECT` | 1 or 2 | FX Channel Select |
| `FX_SELECT` | 1 or 2 | FX Select |

**Mixer / browse buttons** (use `deck=None` unless noted):

| Name | `deck` | Physical button |
|------|--------|----------------|
| `MASTER_CUE` | `None` | Master Cue |
| `BROWSE_LOAD` | 1 or 2 | Load to Deck 1 / 2 |
| `BROWSE_PRESS` | `None` | Browse encoder press |

**Event fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Button name |
| `deck` | `int \| None` | Deck number or `None` |
| `shifted` | `bool` | Whether SHIFT was held |
| `pressed` | `bool` | `True` on press |

---

## on_knob — Absolute knobs and faders

```python
@controller.on_knob(name=None, deck=None)
def handler(event: flx4py.KnobEvent): ...
```

**Available controls:**

| Name | `deck` | Range | Notes |
|------|--------|-------|-------|
| `TEMPO` | 1 or 2 | −1.0 to +1.0 | 0.0 = center |
| `TRIM` | 1 or 2 | 0.0–1.0 | Channel trim knob |
| `EQ_HI` | 1 or 2 | 0.0–1.0 | High EQ |
| `EQ_MID` | 1 or 2 | 0.0–1.0 | Mid EQ |
| `EQ_LOW` | 1 or 2 | 0.0–1.0 | Low EQ |
| `CFX` | 1 or 2 | 0.0–1.0 | Color FX knob |
| `CH_FADER` | 1 or 2 | 0.0–1.0 | Channel fader |
| `FX_LEVEL` | `None` | 0.0–1.0 | FX level/depth |
| `MASTER_LEVEL` | `None` | 0.0–1.0 | Master output level |
| `HEADPHONE_MIX` | `None` | 0.0–1.0 | Headphone cue/master mix |
| `HEADPHONE_LEVEL` | `None` | 0.0–1.0 | Headphone volume |
| `MIC_LEVEL` | `None` | 0.0–1.0 | Microphone level |
| `SMART_FADER` | `None` | 0.0–1.0 | Crossfader curve |
| `CROSSFADER` | `None` | 0.0–1.0 | Crossfader (0 = A, 1 = B) |
| `MONO_STEREO` | `None` | 0.0 or 1.0 | Mono/stereo switch |

**Event fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Control name |
| `deck` | `int \| None` | Deck or `None` for global |
| `value` | `float` | Normalised value (see table) |
| `raw` | `int` | Raw 14-bit (0–16383) or 7-bit (0–127) MIDI value |

---

## on_jog — Jog wheel rotation

```python
@controller.on_jog(deck=None, surface=None)
def handler(event: flx4py.JogEvent): ...
```

| Parameter | Description |
|-----------|-------------|
| `deck` | 1 or 2 |
| `surface` | `'top'` (platter) or `'side'` (outer ring) |

**Event fields:**

| Field | Type | Description |
|-------|------|-------------|
| `deck` | `int` | 1 or 2 |
| `surface` | `str` | `'top'` or `'side'` |
| `direction` | `int` | `+1` = clockwise, `−1` = counter-clockwise |
| `velocity` | `int` | Encoder steps per message (usually 1) |

---

## on_jog_touch — Jog wheel touch

```python
@controller.on_jog_touch(deck=None)
def handler(event: flx4py.JogTouchEvent): ...
```

**Event fields:**

| Field | Type | Description |
|-------|------|-------------|
| `deck` | `int` | 1 or 2 |
| `touched` | `bool` | `True` when touched, `False` when released |

---

## on_browse — Browse encoder

```python
@controller.on_browse(shifted=None)
def handler(event: flx4py.BrowseEvent): ...
```

**Event fields:**

| Field | Type | Description |
|-------|------|-------------|
| `steps` | `int` | Relative steps: positive = right, negative = left |
| `shifted` | `bool` | Whether SHIFT was held |

---

## on_any — Catch all events

```python
@controller.on_any
def catch_all(event):
    print(type(event).__name__, event)
```

This fires for every event regardless of type.

# MIDI Mappings Reference

Complete MIDI mapping table for the Pioneer DDJ-FLX4. These are the raw addresses used internally by flx4py.

!!! note
    You don't need this page to use the library. It's here for reference if you want to understand what's happening under the hood or extend the library.

!!! tip "Official Pioneer reference"
    The full official MIDI message list for the DDJ-FLX4 is available from Pioneer DJ:
    **[DDJ-FLX4 MIDI Message List (PDF)](https://www.pioneerdj.com/-/media/pioneerdj/software-info/controller/ddj-flx4/ddj-flx4_midi_message_list_e1.pdf)**

    Note: some values in the official document differ from what the device actually sends.
    The table below reflects the **real, observed values**.

## Performance Pads

| Deck | Channel | Notes | Description |
|------|---------|-------|-------------|
| 1 | 7 | 48–55 | Pads 0–7 (press: velocity 127, release: velocity 0) |
| 2 | 9 | 48–55 | Pads 0–7 |

For LED output, pads use channels 7 (deck 1 normal), 8 (deck 1 shifted), 9 (deck 2 normal), 10 (deck 2 shifted).

## Pad Mode LED Note Offsets

| Mode | Note offset | Notes |
|------|------------|-------|
| HOT CUE | 0 | Notes 0–7 |
| PAD FX 1 | 16 | Notes 16–23 |
| PAD FX 2 | 32 | Notes 32–39 |
| BEAT JUMP | 48 | Notes 48–55 |
| SAMPLER | 64 | Notes 64–71 |
| KEYBOARD | 80 | Notes 80–87 |
| BEAT LOOP | 96 | Notes 96–103 |
| KEY SHIFT | 112 | Notes 112–119 |

## Tab Keys

| Deck | Channel | Note | Tab |
|------|---------|------|-----|
| 1 | 0 | 27 | HOT CUE (0) |
| 1 | 0 | 30 | PAD FX (1) |
| 1 | 0 | 32 | BEAT JUMP (2) |
| 1 | 0 | 34 | SAMPLER (3) |
| 2 | 1 | 27 | HOT CUE (0) |
| 2 | 1 | 30 | PAD FX (1) |
| 2 | 1 | 32 | BEAT JUMP (2) |
| 2 | 1 | 34 | SAMPLER (3) |

## Jog Wheels

| Deck | Channel | CC | Type | Values |
|------|---------|-----|------|--------|
| 1 | 0 | 34 | Top (platter) rotation | 65 = right, 63 = left |
| 1 | 0 | 33 | Side (outer ring) rotation | 65 = right, 63 = left |
| 1 | 0 | note 54 | Platter touch | 127 = touched, 0 = released |
| 2 | 1 | 34 | Top (platter) rotation | 65 = right, 63 = left |
| 2 | 1 | 33 | Side (outer ring) rotation | 65 = right, 63 = left |
| 2 | 1 | note 54 | Platter touch | 127 = touched, 0 = released |

## Deck Buttons

All buttons use `note_on` messages. Velocity 127 = pressed, velocity 0 = released.

| Name | Deck 1 (ch 0) | Deck 2 (ch 1) | Shifted note |
|------|--------------|--------------|--------------|
| PLAY_PAUSE | 11 | 11 | 14 |
| CUE | 12 | 12 | 72 |
| CUE_LOOP_CALL | 84 | 84 | — |
| IN | 16 | 16 | 76 |
| OUT | 17 | 17 | 78 |
| BEAT_4_EXIT | 77 | 77 | 80 |
| CUE_LOOP_LEFT | 81 | 81 | 62 |
| CUE_LOOP_RIGHT | 83 | 83 | 61 |
| BEAT_SYNC | 88 | 88 | 96 |
| BEAT_SYNC_LONG | 92 | 92 | — |
| SHIFT | 63 | 63 | 104 |

!!! note
    The Pioneer MIDI implementation guide lists different note values for some buttons. The values above are what the device **actually sends** (verified by monitoring).

## FX Buttons

| Name | Channel | Note | Shifted note |
|------|---------|------|--------------|
| FX_BEAT_LEFT | 4 | 99 | 100 |
| FX_BEAT_RIGHT | 4 | 74 | 102 |
| FX_ON_OFF | 4 | 75 | 107 |
| FX_CH_SELECT (CH1) | 4 | 71 | — |
| FX_CH_SELECT (CH2) | 5 | 71 | — |
| FX_SELECT (CH1) | 4 | 67 | — |
| FX_SELECT (CH2) | 5 | 67 | — |

## Mixer / Browse Buttons

| Name | Channel | Note | Shifted note |
|------|---------|------|--------------|
| MASTER_CUE | 6 | 99 | 120 |
| BROWSE_LOAD (deck 1) | 6 | 70 | 66 |
| BROWSE_LOAD (deck 2) | 6 | 71 | 104 |
| BROWSE_PRESS | 6 | 65 | 122 |

## 14-bit Knobs and Faders

All knob/fader controls use paired CC messages: an MSB (coarse) followed immediately by an LSB (fine), yielding 14-bit resolution (0–16383). flx4py fires callbacks only on LSB arrival with the combined value.

| Name | Deck | Channel | MSB CC | LSB CC |
|------|------|---------|---------|---------|
| TEMPO | 1 | 0 | 0 | 32 |
| TRIM | 1 | 0 | 2 | 34 |
| EQ_HI | 1 | 0 | 4 | 36 |
| EQ_MID | 1 | 0 | 7 | 39 |
| EQ_LOW | 1 | 0 | 11 | 43 |
| CFX | 1 | 0 | 15 | 47 |
| CH_FADER | 1 | 0 | 19 | 51 |
| TEMPO | 2 | 1 | 0 | 32 |
| TRIM | 2 | 1 | 2 | 34 |
| EQ_HI | 2 | 1 | 4 | 36 |
| EQ_MID | 2 | 1 | 7 | 39 |
| EQ_LOW | 2 | 1 | 11 | 43 |
| CFX | 2 | 1 | 15 | 47 |
| CH_FADER | 2 | 1 | 19 | 51 |
| FX_LEVEL | — | 4 | 2 | 34 |
| MASTER_LEVEL | — | 6 | 5 | 37 |
| HEADPHONE_MIX | — | 6 | 12 | 44 |
| HEADPHONE_LEVEL | — | 6 | 13 | 45 |
| MIC_LEVEL | — | 6 | 23 | 55 |
| SMART_FADER | — | 6 | 24 | 56 |
| CROSSFADER | — | 6 | 31 | 63 |

`TEMPO` is normalised to −1.0 (slowest) → 0.0 (center) → +1.0 (fastest). All other controls are 0.0–1.0.

## 7-bit Controls

| Name | Channel | CC | Description |
|------|---------|-----|-------------|
| BROWSE_ROTATE | 6 | 64 | Relative encoder: 1–64 = right, 65–127 = left |
| BROWSE_ROTATE (shifted) | 6 | 100 | Same as above but with SHIFT held |
| MONO_STEREO | 6 | 109 | Slider: 0 = stereo, non-zero = mono |

## Level Meter (VU meter output)

VU meters are driven by a CC message on the deck's channel.

| Deck | Channel | CC | Range |
|------|---------|-----|-------|
| 1 | 0 | 2 | 0–127 |
| 2 | 1 | 2 | 0–127 |

Approximate colour thresholds:

| Range | Colour |
|-------|--------|
| 0–37 | Off |
| 38–64 | Green (low) |
| 65–86 | Green (high) |
| 87–100 | Orange (medium) |
| 101–118 | Orange (high) |
| 119–127 | Red (peak) |

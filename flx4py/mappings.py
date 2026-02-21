"""
MIDI mappings for the Pioneer DDJ-FLX4.

All input and output MIDI addresses are defined here. Input mappings decode
incoming messages from the controller; output mappings are used to send LED
commands back to it.
"""

from typing import NamedTuple


class ButtonInfo(NamedTuple):
    name: str
    deck: int | None  # None = global (FX, mixer, browse)
    shifted: bool


class KnobInfo(NamedTuple):
    name: str
    deck: int | None
    lsb_cc: int | None   # None for 7-bit absolute controls
    relative: bool        # True for encoders (browse)


class JogInfo(NamedTuple):
    deck: int
    surface: str  # 'top' or 'side'


# ---------------------------------------------------------------------------
# Input mappings
# ---------------------------------------------------------------------------

# (channel, note) -> (deck, pad_index)
PAD_INPUT: dict[tuple[int, int], tuple[int, int]] = {
    **{(7, 48 + i): (1, i) for i in range(8)},
    **{(9, 48 + i): (2, i) for i in range(8)},
}

# (channel, note) -> (deck, tab_index)
TAB_INPUT: dict[tuple[int, int], tuple[int, int]] = {
    (0, 27): (1, 0), (0, 30): (1, 1), (0, 32): (1, 2), (0, 34): (1, 3),
    (1, 27): (2, 0), (1, 30): (2, 1), (1, 32): (2, 2), (1, 34): (2, 3),
}

# (channel, control) -> JogInfo  (control_change)
JOG_INPUT: dict[tuple[int, int], JogInfo] = {
    (0, 34): JogInfo(deck=1, surface='top'),
    (0, 33): JogInfo(deck=1, surface='side'),
    (1, 34): JogInfo(deck=2, surface='top'),
    (1, 33): JogInfo(deck=2, surface='side'),
}

# (channel, note) -> deck  (note_on)
JOG_TOUCH_INPUT: dict[tuple[int, int], int] = {
    (0, 54): 1,
    (1, 54): 2,
}

# (channel, note) -> ButtonInfo  (note_on)
BUTTON_INPUT: dict[tuple[int, int], ButtonInfo] = {
    # Deck 1
    (0, 11):  ButtonInfo('PLAY_PAUSE',      1,    False),
    (0, 14):  ButtonInfo('PLAY_PAUSE',      1,    True),
    (0, 12):  ButtonInfo('CUE',             1,    False),
    (0, 72):  ButtonInfo('CUE',             1,    True),
    (0, 84):  ButtonInfo('CUE_LOOP_CALL',   1,    False),
    (0, 16):  ButtonInfo('IN',              1,    False),
    (0, 76):  ButtonInfo('IN',              1,    True),
    (0, 17):  ButtonInfo('OUT',             1,    False),
    (0, 78):  ButtonInfo('OUT',             1,    True),
    (0, 77):  ButtonInfo('BEAT_4_EXIT',     1,    False),
    (0, 80):  ButtonInfo('BEAT_4_EXIT',     1,    True),
    (0, 81):  ButtonInfo('CUE_LOOP_LEFT',   1,    False),
    (0, 62):  ButtonInfo('CUE_LOOP_LEFT',   1,    True),
    (0, 83):  ButtonInfo('CUE_LOOP_RIGHT',  1,    False),
    (0, 61):  ButtonInfo('CUE_LOOP_RIGHT',  1,    True),
    (0, 88):  ButtonInfo('BEAT_SYNC',       1,    False),
    (0, 92):  ButtonInfo('BEAT_SYNC_LONG',  1,    False),
    (0, 96):  ButtonInfo('BEAT_SYNC',       1,    True),
    (0, 63):  ButtonInfo('SHIFT',           1,    False),
    (0, 104): ButtonInfo('SHIFT',           1,    True),

    # Deck 2
    (1, 11):  ButtonInfo('PLAY_PAUSE',      2,    False),
    (1, 14):  ButtonInfo('PLAY_PAUSE',      2,    True),
    (1, 12):  ButtonInfo('CUE',             2,    False),
    (1, 72):  ButtonInfo('CUE',             2,    True),
    (1, 84):  ButtonInfo('CUE_LOOP_CALL',   2,    False),
    (1, 16):  ButtonInfo('IN',              2,    False),
    (1, 76):  ButtonInfo('IN',              2,    True),
    (1, 17):  ButtonInfo('OUT',             2,    False),
    (1, 78):  ButtonInfo('OUT',             2,    True),
    (1, 77):  ButtonInfo('BEAT_4_EXIT',     2,    False),
    (1, 80):  ButtonInfo('BEAT_4_EXIT',     2,    True),
    (1, 81):  ButtonInfo('CUE_LOOP_LEFT',   2,    False),
    (1, 62):  ButtonInfo('CUE_LOOP_LEFT',   2,    True),
    (1, 83):  ButtonInfo('CUE_LOOP_RIGHT',  2,    False),
    (1, 61):  ButtonInfo('CUE_LOOP_RIGHT',  2,    True),
    (1, 88):  ButtonInfo('BEAT_SYNC',       2,    False),
    (1, 92):  ButtonInfo('BEAT_SYNC_LONG',  2,    False),
    (1, 96):  ButtonInfo('BEAT_SYNC',       2,    True),
    (1, 63):  ButtonInfo('SHIFT',           2,    False),
    (1, 104): ButtonInfo('SHIFT',           2,    True),

    # FX buttons (no deck for the global ones)
    (4, 99):  ButtonInfo('FX_BEAT_LEFT',    None, False),
    (4, 100): ButtonInfo('FX_BEAT_LEFT',    None, True),
    (4, 74):  ButtonInfo('FX_BEAT_RIGHT',   None, False),
    (4, 102): ButtonInfo('FX_BEAT_RIGHT',   None, True),
    (4, 75):  ButtonInfo('FX_ON_OFF',       None, False),
    (4, 107): ButtonInfo('FX_ON_OFF',       None, True),
    (4, 71):  ButtonInfo('FX_CH_SELECT',    1,    False),
    (5, 71):  ButtonInfo('FX_CH_SELECT',    2,    False),
    (4, 67):  ButtonInfo('FX_SELECT',       1,    False),
    (5, 67):  ButtonInfo('FX_SELECT',       2,    False),

    # Mixer
    (6, 99):  ButtonInfo('MASTER_CUE',      None, False),
    (6, 120): ButtonInfo('MASTER_CUE',      None, True),

    # Browse
    (6, 70):  ButtonInfo('BROWSE_LOAD',     1,    False),
    (6, 66):  ButtonInfo('BROWSE_LOAD',     1,    True),
    (6, 71):  ButtonInfo('BROWSE_LOAD',     2,    False),
    (6, 104): ButtonInfo('BROWSE_LOAD',     2,    True),
    (6, 65):  ButtonInfo('BROWSE_PRESS',    None, False),
    (6, 122): ButtonInfo('BROWSE_PRESS',    None, True),
}

# (channel, msb_cc) -> KnobInfo  (14-bit control_change)
KNOB_14BIT_INPUT: dict[tuple[int, int], KnobInfo] = {
    (0, 0):  KnobInfo('TEMPO',           1,    32,   False),
    (0, 2):  KnobInfo('TRIM',            1,    34,   False),
    (0, 4):  KnobInfo('EQ_HI',          1,    36,   False),
    (0, 7):  KnobInfo('EQ_MID',         1,    39,   False),
    (0, 11): KnobInfo('EQ_LOW',         1,    43,   False),
    (0, 15): KnobInfo('CFX',            1,    47,   False),
    (0, 19): KnobInfo('CH_FADER',       1,    51,   False),

    (1, 0):  KnobInfo('TEMPO',           2,    32,   False),
    (1, 2):  KnobInfo('TRIM',            2,    34,   False),
    (1, 4):  KnobInfo('EQ_HI',          2,    36,   False),
    (1, 7):  KnobInfo('EQ_MID',         2,    39,   False),
    (1, 11): KnobInfo('EQ_LOW',         2,    43,   False),
    (1, 15): KnobInfo('CFX',            2,    47,   False),
    (1, 19): KnobInfo('CH_FADER',       2,    51,   False),

    (4, 2):  KnobInfo('FX_LEVEL',       None, 34,   False),
    (6, 5):  KnobInfo('MASTER_LEVEL',   None, 37,   False),
    (6, 12): KnobInfo('HEADPHONE_MIX',  None, 44,   False),
    (6, 13): KnobInfo('HEADPHONE_LEVEL', None, 45,  False),
    (6, 23): KnobInfo('MIC_LEVEL',      None, 55,   False),
    (6, 24): KnobInfo('SMART_FADER',    None, 56,   False),
    (6, 31): KnobInfo('CROSSFADER',     None, 63,   False),
}

# Reverse LSB lookup: (channel, lsb_cc) -> (channel, msb_cc)
KNOB_14BIT_LSB: dict[tuple[int, int], tuple[int, int]] = {
    (ch, info.lsb_cc): (ch, msb_cc)
    for (ch, msb_cc), info in KNOB_14BIT_INPUT.items()
    if info.lsb_cc is not None
}

# 7-bit absolute (MONO_STEREO slider)
KNOB_7BIT_INPUT: dict[tuple[int, int], KnobInfo] = {
    (6, 109): KnobInfo('MONO_STEREO', None, None, False),
}

# Browse encoder (relative)
BROWSE_INPUT: dict[tuple[int, int], bool] = {
    (6, 64):  False,   # normal
    (6, 100): True,    # shifted
}

# ---------------------------------------------------------------------------
# LED output mappings
# ---------------------------------------------------------------------------

# Pad LED channels per deck: deck -> (normal_ch, shifted_ch)
PAD_LED_CHANNELS: dict[int, tuple[int, int]] = {1: (7, 8), 2: (9, 10)}

# Pad LED note offsets per mode
PAD_LED_MODES: dict[str, int] = {
    'HOT_CUE':   0,
    'PAD_FX_1':  16,
    'PAD_FX_2':  32,
    'BEAT_JUMP': 48,
    'SAMPLER':   64,
    'KEYBOARD':  80,
    'BEAT_LOOP': 96,
    'KEY_SHIFT': 112,
}

# Button LED: (name, deck_or_none, shifted) -> (channel, note)
# Derived from BUTTON_INPUT — the same MIDI address is used for both.
BUTTON_LED: dict[tuple[str, int | None, bool], tuple[int, int]] = {
    (info.name, info.deck, info.shifted): (ch, note)
    for (ch, note), info in BUTTON_INPUT.items()
}

# Level meter CC number (sent on channel 0 for deck 1, channel 1 for deck 2)
LEVEL_METER_CC = 2

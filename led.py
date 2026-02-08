import mido
import time
from enum import Enum


class LEDState(Enum):
    """LED state enumeration"""
    OFF = 0x00
    ON = 0x7F


class FLX4LEDController:
    """
    Control LEDs on the Pioneer DDJ-FLX4 DJ Controller.

    This class allows you to control all button and pad LEDs by sending
    MIDI messages back to the controller.
    """

    # Performance Pad mappings for each mode
    # Channel 7 = Deck 1 normal, Channel 8 = Deck 1 shift
    # Channel 9 = Deck 2 normal, Channel 10 = Deck 2 shift
    PAD_NOTES = {
        'HOT_CUE': list(range(0, 8)),      # Notes 0-7
        'PAD_FX_1': list(range(16, 24)),   # Notes 16-23
        'PAD_FX_2': list(range(32, 40)),   # Notes 32-39
        'BEAT_JUMP': list(range(48, 56)),  # Notes 48-55
        'SAMPLER': list(range(64, 72)),    # Notes 64-71
        'KEYBOARD': list(range(80, 88)),   # Notes 80-87
        'BEAT_LOOP': list(range(96, 104)),  # Notes 96-103
        'KEY_SHIFT': list(range(112, 120))  # Notes 112-119
    }

    # Button note mappings
    BUTTONS = {
        # Deck buttons (channel 0 = Deck 1, channel 1 = Deck 2)
        'PLAY_PAUSE': 11,
        'PLAY_PAUSE_SHIFT': 14,
        'CUE': 12,
        'CUE_SHIFT': 72,
        'CUE_LOOP_CALL': 84,  # Actual value (manual says 63)
        'SHIFT': 63,          # Actual value (manual says 84)
        'SHIFT_SHIFT': 104,
        'IN': 16,
        'IN_SHIFT': 76,
        'OUT': 17,
        'OUT_SHIFT': 78,
        'BEAT_4_EXIT': 77,
        'BEAT_4_EXIT_SHIFT': 80,
        'CUE_LOOP_LEFT': 81,
        'CUE_LOOP_LEFT_SHIFT': 62,
        'CUE_LOOP_RIGHT': 83,
        'CUE_LOOP_RIGHT_SHIFT': 61,
        'BEAT_SYNC': 88,
        'BEAT_SYNC_SHIFT': 96,

        # TAB buttons (channel 0 = Deck 1, channel 1 = Deck 2)
        'TAB_0': 27,
        'TAB_1': 30,
        'TAB_2': 32,
        'TAB_3': 34,

        # FX buttons (channel 4 for CH1, channel 5 for CH2)
        'FX_BEAT_LEFT': 99,
        'FX_BEAT_LEFT_SHIFT': 100,
        'FX_BEAT_RIGHT': 74,
        'FX_BEAT_RIGHT_SHIFT': 102,
        'FX_ON_OFF': 75,
        'FX_ON_OFF_SHIFT': 107,
        'FX_CH_SELECT': 71,
        'FX_SELECT': 67,

        # Mixer buttons (channel 6)
        'MASTER_CUE': 99,
        'MASTER_CUE_SHIFT': 120,

        # Browse buttons (channel 6)
        'BROWSE_LOAD_DECK_1': 70,
        'BROWSE_LOAD_DECK_1_SHIFT': 66,
        'BROWSE_LOAD_DECK_2': 71,
        'BROWSE_LOAD_DECK_2_SHIFT': 104,
        'BROWSE_PRESS': 65,
        'BROWSE_PRESS_SHIFT': 122,
    }

    # Volume meter levels
    # Channel level meter note is 2 for both decks
    LEVEL_METER_NOTE = 2

    # Volume meter ranges (velocity values)
    METER_RANGES = {
        'OFF': 0x00,
        'GREEN1_MIN': 0x26,   # 38
        'GREEN1_MAX': 0x40,   # 64
        'GREEN2_MIN': 0x41,   # 65
        'GREEN2_MAX': 0x56,   # 86
        'ORANGE1_MIN': 0x57,  # 87
        'ORANGE1_MAX': 0x64,  # 100
        'ORANGE2_MIN': 0x65,  # 101
        'ORANGE2_MAX': 0x76,  # 118
        'RED_MIN': 0x77,      # 119
        'RED_MAX': 0x7F,      # 127
    }

    def __init__(self, name_keyword: str = "FLX4"):
        """
        Initialize the LED controller.

        Args:
            name_keyword: Keyword to find the FLX4 MIDI output port
        """
        self.name = self.find_device(name_keyword)
        if not self.name:
            raise RuntimeError("FLX4 output port not found")
        self.output = mido.open_output(self.name)
        print(f"Connected to: {self.name}")

    @staticmethod
    def find_device(keyword: str) -> str | None:
        """Find the MIDI output device matching the keyword"""
        for name in mido.get_output_names():
            if keyword in name:
                return name
        return None

    def _send_note(self, channel: int, note: int, velocity: int):
        """Send a note_on message to control an LED"""
        msg = mido.Message('note_on', channel=channel,
                           note=note, velocity=velocity)
        self.output.send(msg)

    def _send_cc(self, channel: int, control: int, value: int):
        """Send a control_change message"""
        msg = mido.Message('control_change', channel=channel,
                           control=control, value=value)
        self.output.send(msg)

    # ==================== Performance Pads ====================

    def set_pad(self, deck: int, pad_index: int, state: LEDState, mode: str = 'HOT_CUE', shifted: bool = False):
        """
        Set a performance pad LED.

        Args:
            deck: 1 or 2
            pad_index: 0-7 (pad number)
            state: LEDState.ON or LEDState.OFF
            mode: Pad mode ('HOT_CUE', 'PAD_FX_1', 'BEAT_JUMP', 'SAMPLER', etc.)
            shifted: True if shift is held
        """
        if deck not in [1, 2]:
            raise ValueError("Deck must be 1 or 2")
        if pad_index < 0 or pad_index > 7:
            raise ValueError("Pad index must be 0-7")
        if mode not in self.PAD_NOTES:
            raise ValueError(f"Invalid mode. Must be one of: {
                             list(self.PAD_NOTES.keys())}")

        # Determine channel: Deck 1 = 7/8, Deck 2 = 9/10
        base_channel = 7 if deck == 1 else 9
        channel = base_channel + (1 if shifted else 0)

        note = self.PAD_NOTES[mode][pad_index]
        self._send_note(channel, note, state.value)

    def set_all_pads(self, deck: int, state: LEDState, mode: str = 'HOT_CUE', shifted: bool = False):
        """
        Set all 8 pads in a mode to the same state.

        Args:
            deck: 1 or 2
            state: LEDState.ON or LEDState.OFF
            mode: Pad mode
            shifted: True if shift is held
        """
        for i in range(8):
            self.set_pad(deck, i, state, mode, shifted)

    def clear_all_pads(self, deck: int, mode: str = 'HOT_CUE'):
        """Clear all pads in a mode (both normal and shifted)"""
        self.set_all_pads(deck, LEDState.OFF, mode, shifted=False)
        self.set_all_pads(deck, LEDState.OFF, mode, shifted=True)

    # ==================== Deck Buttons ====================

    def set_deck_button(self, deck: int, button: str, state: LEDState):
        """
        Set a deck button LED.

        Args:
            deck: 1 or 2
            button: Button name (e.g., 'PLAY_PAUSE', 'CUE', 'BEAT_SYNC')
            state: LEDState.ON or LEDState.OFF
        """
        if deck not in [1, 2]:
            raise ValueError("Deck must be 1 or 2")
        if button not in self.BUTTONS:
            raise ValueError(f"Unknown button: {button}")

        channel = 0 if deck == 1 else 1
        note = self.BUTTONS[button]
        self._send_note(channel, note, state.value)

    def set_tab_button(self, deck: int, tab_index: int, state: LEDState):
        """
        Set a TAB button LED.

        Args:
            deck: 1 or 2
            tab_index: 0-3
            state: LEDState.ON or LEDState.OFF
        """
        if deck not in [1, 2]:
            raise ValueError("Deck must be 1 or 2")
        if tab_index < 0 or tab_index > 3:
            raise ValueError("Tab index must be 0-3")

        channel = 0 if deck == 1 else 1
        note = self.BUTTONS[f'TAB_{tab_index}']
        self._send_note(channel, note, state.value)

    # ==================== FX Buttons ====================

    def set_fx_button(self, button: str, state: LEDState, channel_select: int = 1):
        """
        Set an FX button LED.

        Args:
            button: 'FX_BEAT_LEFT', 'FX_BEAT_RIGHT', 'FX_ON_OFF', 'FX_CH_SELECT', or 'FX_SELECT'
            state: LEDState.ON or LEDState.OFF
            channel_select: 1 for CH1, 2 for CH2 (only for FX_CH_SELECT and FX_SELECT)
        """
        if button not in self.BUTTONS or not button.startswith('FX_'):
            raise ValueError(f"Unknown FX button: {button}")

        # CH SELECT and SELECT buttons use different channels for CH1/CH2
        if button in ['FX_CH_SELECT', 'FX_SELECT']:
            channel = 4 if channel_select == 1 else 5
        else:
            channel = 4  # Other FX buttons always use channel 4

        note = self.BUTTONS[button]
        self._send_note(channel, note, state.value)

    def set_fx_on_off_blink(self):
        """
        Make the FX ON/OFF button blink (send ON, it will blink until you send OFF)
        Note: According to manual, button blinks when NOTE ON received, 
        lights solid when NOTE OFF received.
        """
        self._send_note(4, self.BUTTONS['FX_ON_OFF'], LEDState.ON.value)

    # ==================== Mixer/Browse Buttons ====================

    def set_mixer_button(self, button: str, state: LEDState):
        """
        Set a mixer button LED.

        Args:
            button: 'MASTER_CUE' or shift variant
            state: LEDState.ON or LEDState.OFF
        """
        if button not in self.BUTTONS:
            raise ValueError(f"Unknown mixer button: {button}")

        note = self.BUTTONS[button]
        self._send_note(6, note, state.value)

    def set_browse_button(self, button: str, state: LEDState):
        """
        Set a browse button LED.

        Args:
            button: 'BROWSE_LOAD_DECK_1', 'BROWSE_LOAD_DECK_2', 'BROWSE_PRESS', or shift variants
            state: LEDState.ON or LEDState.OFF
        """
        if button not in self.BUTTONS or not button.startswith('BROWSE_'):
            raise ValueError(f"Unknown browse button: {button}")

        note = self.BUTTONS[button]
        self._send_note(6, note, state.value)

    # ==================== Volume Meters ====================

    def set_level_meter(self, deck: int, level: int):
        """
        Set the channel level meter (VU meter) for a deck.

        Args:
            deck: 1 or 2
            level: 0-127 (velocity value)
                   0-37: Off
                   38-64: Green (low)
                   65-86: Green (higher)
                   87-100: Orange (medium)
                   101-118: Orange (high)
                   119-127: Red (peak)
        """
        if deck not in [1, 2]:
            raise ValueError("Deck must be 1 or 2")
        if level < 0 or level > 127:
            raise ValueError("Level must be 0-127")

        channel = 0 if deck == 1 else 1
        # Volume meter uses CC message, not note_on!
        self._send_cc(channel, self.LEVEL_METER_NOTE, level)

    def set_level_meter_normalized(self, deck: int, level: float):
        """
        Set the channel level meter using a normalized value.

        Args:
            deck: 1 or 2
            level: 0.0-1.0 (will be mapped to 0-127)
        """
        if level < 0.0 or level > 1.0:
            raise ValueError("Level must be 0.0-1.0")

        velocity = int(level * 127)
        self.set_level_meter(deck, velocity)

    def set_level_meter_color(self, deck: int, color: str):
        """
        Set the channel level meter to a specific color level.

        Args:
            deck: 1 or 2
            color: 'OFF', 'GREEN1', 'GREEN2', 'ORANGE1', 'ORANGE2', or 'RED'
        """
        color_map = {
            'OFF': 0,
            'GREEN1': self.METER_RANGES['GREEN1_MAX'],
            'GREEN2': self.METER_RANGES['GREEN2_MAX'],
            'ORANGE1': self.METER_RANGES['ORANGE1_MAX'],
            'ORANGE2': self.METER_RANGES['ORANGE2_MAX'],
            'RED': self.METER_RANGES['RED_MAX']
        }

        if color not in color_map:
            raise ValueError(f"Color must be one of: {list(color_map.keys())}")

        self.set_level_meter(deck, color_map[color])

    def animate_meter(self, deck: int, duration: float = 2.0, steps: int = 50):
        """
        Animate the level meter from off to red and back.

        Args:
            deck: 1 or 2
            duration: Total duration in seconds
            steps: Number of steps in the animation
        """
        delay = duration / (steps * 2)

        # Ramp up
        for i in range(steps):
            level = int((i / steps) * 127)
            self.set_level_meter(deck, level)
            time.sleep(delay)

        # Ramp down
        for i in range(steps, -1, -1):
            level = int((i / steps) * 127)
            self.set_level_meter(deck, level)
            time.sleep(delay)

    # ==================== Utility Functions ====================

    def all_leds_off(self):
        """Turn off all LEDs on the controller"""
        print("Turning off all LEDs...")

        # Turn off volume meters
        for deck in [1, 2]:
            self.set_level_meter(deck, 0)

        # Turn off all pads for both decks in all modes
        for deck in [1, 2]:
            for mode in self.PAD_NOTES.keys():
                self.clear_all_pads(deck, mode)

        # Turn off all deck buttons
        for deck in [1, 2]:
            for button in ['PLAY_PAUSE', 'PLAY_PAUSE_SHIFT', 'CUE', 'CUE_SHIFT',
                           'CUE_LOOP_CALL', 'SHIFT', 'SHIFT_SHIFT', 'IN', 'IN_SHIFT',
                           'OUT', 'OUT_SHIFT', 'BEAT_4_EXIT', 'BEAT_4_EXIT_SHIFT',
                           'CUE_LOOP_LEFT', 'CUE_LOOP_LEFT_SHIFT', 'CUE_LOOP_RIGHT',
                           'CUE_LOOP_RIGHT_SHIFT', 'BEAT_SYNC', 'BEAT_SYNC_SHIFT']:
                try:
                    self.set_deck_button(deck, button, LEDState.OFF)
                except:
                    pass

            # Turn off TAB buttons
            for i in range(4):
                self.set_tab_button(deck, i, LEDState.OFF)

        # Turn off FX buttons
        for button in ['FX_BEAT_LEFT', 'FX_BEAT_RIGHT', 'FX_ON_OFF']:
            self.set_fx_button(button, LEDState.OFF)

        for ch in [1, 2]:
            self.set_fx_button('FX_CH_SELECT', LEDState.OFF, ch)
            self.set_fx_button('FX_SELECT', LEDState.OFF, ch)

        # Turn off mixer/browse buttons
        for button in ['MASTER_CUE', 'BROWSE_LOAD_DECK_1', 'BROWSE_LOAD_DECK_2', 'BROWSE_PRESS']:
            try:
                if 'MASTER' in button:
                    self.set_mixer_button(button, LEDState.OFF)
                else:
                    self.set_browse_button(button, LEDState.OFF)
            except:
                pass

        print("All LEDs turned off")

    def test_pattern(self, delay: float = 0.2):
        """
        Run a test pattern to verify LED control.

        Args:
            delay: Delay between LED changes in seconds (default: 0.2 for slower animation)
        """
        print("Running LED test pattern...")

        # Test volume meters first
        print("\nTesting volume meters...")
        for deck in [1, 2]:
            print(f"  Deck {deck} meter: Green1")
            self.set_level_meter_color(deck, 'GREEN1')
            time.sleep(delay * 3)

            print(f"  Deck {deck} meter: Green2")
            self.set_level_meter_color(deck, 'GREEN2')
            time.sleep(delay * 3)

            print(f"  Deck {deck} meter: Orange1")
            self.set_level_meter_color(deck, 'ORANGE1')
            time.sleep(delay * 3)

            print(f"  Deck {deck} meter: Orange2")
            self.set_level_meter_color(deck, 'ORANGE2')
            time.sleep(delay * 3)

            print(f"  Deck {deck} meter: Red (peak)")
            self.set_level_meter_color(deck, 'RED')
            time.sleep(delay * 3)

            print(f"  Deck {deck} meter: Off")
            self.set_level_meter_color(deck, 'OFF')
            time.sleep(delay * 2)

        # Animate both meters together
        print("\nAnimating both meters together...")
        for i in range(128):
            self.set_level_meter(1, i)
            self.set_level_meter(2, i)
            time.sleep(0.01)

        for i in range(127, -1, -1):
            self.set_level_meter(1, i)
            self.set_level_meter(2, i)
            time.sleep(0.01)

        time.sleep(delay * 2)

        # Test pads - light up each pad sequentially
        print("\nTesting performance pads...")
        for deck in [1, 2]:
            print(f"  Deck {deck} pads...")
            for i in range(8):
                self.set_pad(deck, i, LEDState.ON, mode='HOT_CUE')
                time.sleep(delay)
                self.set_pad(deck, i, LEDState.OFF, mode='HOT_CUE')

        # Test TAB buttons
        print("\nTesting TAB buttons...")
        for deck in [1, 2]:
            print(f"  Deck {deck} TABs...")
            for i in range(4):
                self.set_tab_button(deck, i, LEDState.ON)
                time.sleep(delay)
                self.set_tab_button(deck, i, LEDState.OFF)

        # Test main deck buttons
        print("\nTesting deck control buttons...")
        for deck in [1, 2]:
            print(f"  Deck {deck} buttons...")
            for button in ['PLAY_PAUSE', 'CUE', 'BEAT_SYNC', 'SHIFT']:
                self.set_deck_button(deck, button, LEDState.ON)
                time.sleep(delay)
                self.set_deck_button(deck, button, LEDState.OFF)

        # Test FX buttons
        print("\nTesting FX buttons...")
        self.set_fx_button('FX_ON_OFF', LEDState.ON)
        time.sleep(delay * 2)
        self.set_fx_button('FX_ON_OFF', LEDState.OFF)

        # Test browse buttons
        print("\nTesting browse buttons...")
        self.set_browse_button('BROWSE_LOAD_DECK_1', LEDState.ON)
        time.sleep(delay)
        self.set_browse_button('BROWSE_LOAD_DECK_1', LEDState.OFF)

        self.set_browse_button('BROWSE_LOAD_DECK_2', LEDState.ON)
        time.sleep(delay)
        self.set_browse_button('BROWSE_LOAD_DECK_2', LEDState.OFF)

        print("\nTest pattern complete!")

    # ==================== Screensaver / Standby Animations ====================

    def screensaver_random_pads(self, duration: float = 60.0, speed: float = 0.1):
        """
        Random twinkling pads animation.

        Args:
            duration: How long to run the animation in seconds
            speed: Delay between changes in seconds
        """
        import random
        print(f"Running random pads screensaver for {duration}s...")

        start_time = time.time()
        active_pads = {}  # Track which pads are on

        while time.time() - start_time < duration:
            # Randomly turn on/off pads
            deck = random.choice([1, 2])
            pad = random.randint(0, 7)
            mode = random.choice(list(self.PAD_NOTES.keys()))

            key = (deck, pad, mode)

            if key in active_pads:
                # Turn off
                self.set_pad(deck, pad, LEDState.OFF, mode)
                del active_pads[key]
            else:
                # Turn on
                self.set_pad(deck, pad, LEDState.ON, mode)
                active_pads[key] = True

            time.sleep(speed)

        # Clean up
        for deck, pad, mode in active_pads:
            self.set_pad(deck, pad, LEDState.OFF, mode)

    def screensaver_wave(self, duration: float = 60.0, speed: float = 0.05):
        """
        Wave animation across pads.

        Args:
            duration: How long to run the animation in seconds
            speed: Speed of the wave
        """
        print(f"Running wave screensaver for {duration}s...")

        start_time = time.time()
        position = 0

        while time.time() - start_time < duration:
            # Clear all pads
            for deck in [1, 2]:
                for i in range(8):
                    self.set_pad(deck, i, LEDState.OFF, mode='HOT_CUE')

            # Light up wave position
            for deck in [1, 2]:
                self.set_pad(deck, position % 8, LEDState.ON, mode='HOT_CUE')

            position += 1
            time.sleep(speed)

        self.all_leds_off()

    def screensaver_breathing(self, duration: float = 60.0, breath_speed: float = 2.0):
        """
        Breathing animation with volume meters and pads.

        Args:
            duration: How long to run the animation in seconds
            breath_speed: Duration of one breath cycle in seconds
        """
        print(f"Running breathing screensaver for {duration}s...")

        start_time = time.time()

        while time.time() - start_time < duration:
            # Breathe in
            steps = 50
            for i in range(steps):
                level = int((i / steps) * 127)
                num_pads = int((i / steps) * 8)

                self.set_level_meter(1, level)
                self.set_level_meter(2, level)

                for deck in [1, 2]:
                    for pad in range(8):
                        state = LEDState.ON if pad < num_pads else LEDState.OFF
                        self.set_pad(deck, pad, state, mode='HOT_CUE')

                time.sleep(breath_speed / (steps * 2))

            # Breathe out
            for i in range(steps, -1, -1):
                level = int((i / steps) * 127)
                num_pads = int((i / steps) * 8)

                self.set_level_meter(1, level)
                self.set_level_meter(2, level)

                for deck in [1, 2]:
                    for pad in range(8):
                        state = LEDState.ON if pad < num_pads else LEDState.OFF
                        self.set_pad(deck, pad, state, mode='HOT_CUE')

                time.sleep(breath_speed / (steps * 2))

        self.all_leds_off()

    def screensaver_knight_rider(self, duration: float = 60.0, speed: float = 0.05):
        """
        Knight Rider / Cylon style scanning animation.

        Args:
            duration: How long to run the animation in seconds
            speed: Speed of the scanner
        """
        print(f"Running Knight Rider screensaver for {duration}s...")

        start_time = time.time()

        while time.time() - start_time < duration:
            # Scan left to right
            for i in range(8):
                for deck in [1, 2]:
                    for pad in range(8):
                        state = LEDState.ON if pad == i else LEDState.OFF
                        self.set_pad(deck, pad, state, mode='HOT_CUE')

                # Update meter to follow
                level = int((i / 7) * 127)
                self.set_level_meter(1, level)
                self.set_level_meter(2, level)

                time.sleep(speed)

            # Scan right to left
            for i in range(6, 0, -1):
                for deck in [1, 2]:
                    for pad in range(8):
                        state = LEDState.ON if pad == i else LEDState.OFF
                        self.set_pad(deck, pad, state, mode='HOT_CUE')

                level = int((i / 7) * 127)
                self.set_level_meter(1, level)
                self.set_level_meter(2, level)

                time.sleep(speed)

        self.all_leds_off()

    def screensaver_pulse_buttons(self, duration: float = 60.0, speed: float = 0.5):
        """
        Pulse all buttons on and off.

        Args:
            duration: How long to run the animation in seconds
            speed: Pulse speed in seconds
        """
        print(f"Running pulse buttons screensaver for {duration}s...")

        start_time = time.time()
        state = True

        while time.time() - start_time < duration:
            led_state = LEDState.ON if state else LEDState.OFF

            # Pulse all deck buttons
            for deck in [1, 2]:
                for button in ['PLAY_PAUSE', 'CUE', 'BEAT_SYNC']:
                    try:
                        self.set_deck_button(deck, button, led_state)
                    except:
                        pass

                for i in range(4):
                    self.set_tab_button(deck, i, led_state)

            # Pulse FX
            self.set_fx_button('FX_ON_OFF', led_state)

            # Pulse browse
            self.set_browse_button('BROWSE_LOAD_DECK_1', led_state)
            self.set_browse_button('BROWSE_LOAD_DECK_2', led_state)

            state = not state
            time.sleep(speed)

        self.all_leds_off()

    def screensaver_rainbow_chase(self, duration: float = 60.0, speed: float = 0.08):
        """
        Rainbow-like chase pattern across both decks.

        Args:
            duration: How long to run the animation in seconds
            speed: Speed of the chase
        """
        print(f"Running rainbow chase screensaver for {duration}s...")

        start_time = time.time()
        offset = 0

        while time.time() - start_time < duration:
            for deck in [1, 2]:
                for i in range(8):
                    # Create a moving pattern
                    position = (i + offset + (deck - 1) * 4) % 16
                    state = LEDState.ON if position < 4 else LEDState.OFF
                    self.set_pad(deck, i, state, mode='HOT_CUE')

            # Animate meters in sync
            meter_level = int((abs(8 - (offset % 16)) / 8) * 127)
            self.set_level_meter(1, meter_level)
            self.set_level_meter(2, 127 - meter_level)

            offset += 1
            time.sleep(speed)

        self.all_leds_off()

    def screensaver_random_mix(self, duration: float = 300.0):
        """
        Mix of different animations, changing every 30 seconds.

        Args:
            duration: Total duration in seconds (default: 5 minutes)
        """
        import random

        animations = [
            ('Random Pads', lambda: self.screensaver_random_pads(30, 0.1)),
            ('Wave', lambda: self.screensaver_wave(30, 0.05)),
            ('Breathing', lambda: self.screensaver_breathing(30, 2.0)),
            ('Knight Rider', lambda: self.screensaver_knight_rider(30, 0.05)),
            ('Pulse Buttons', lambda: self.screensaver_pulse_buttons(30, 0.5)),
            ('Rainbow Chase', lambda: self.screensaver_rainbow_chase(30, 0.08)),
        ]

        print(f"Running mixed screensaver for {
              duration}s (changing every 30s)...")

        start_time = time.time()

        while time.time() - start_time < duration:
            name, animation = random.choice(animations)
            print(f"  Now playing: {name}")
            try:
                animation()
            except KeyboardInterrupt:
                raise
            except:
                pass

            self.all_leds_off()
            time.sleep(0.5)

        self.all_leds_off()

    def screensaver_mode(self):
        """
        Run continuous animated patterns as a screensaver/standby mode.
        Cycles through different effects until interrupted with Ctrl+C.
        """
        import random

        effects = [
            self._screensaver_wave,
            self._screensaver_pulse,
            self._screensaver_chase,
            self._screensaver_random_pads,
            self._screensaver_vu_meters,
            self._screensaver_ping_pong,
            self._screensaver_sparkle,
        ]

        print("\n╔════════════════════════════════════════╗")
        print("║  SCREENSAVER MODE - Press Ctrl+C to  ║")
        print("║  exit and turn off all LEDs          ║")
        print("╚════════════════════════════════════════╝\n")

        try:
            while True:
                # Pick a random effect and run it
                effect = random.choice(effects)
                effect()
                time.sleep(0.5)  # Brief pause between effects
        except KeyboardInterrupt:
            print("\n\nExiting screensaver mode...")

    def _screensaver_wave(self):
        """Wave effect across pads"""
        print("Effect: Wave")
        for _ in range(3):  # Run 3 cycles
            for i in range(8):
                self.set_pad(1, i, LEDState.ON, mode='HOT_CUE')
                self.set_pad(2, i, LEDState.ON, mode='HOT_CUE')
                time.sleep(0.08)
                self.set_pad(1, i, LEDState.OFF, mode='HOT_CUE')
                self.set_pad(2, i, LEDState.OFF, mode='HOT_CUE')

    def _screensaver_pulse(self):
        """Pulse all pads and buttons together"""
        print("Effect: Pulse")
        for _ in range(2):
            # Fade in
            for i in range(0, 128, 8):
                self.set_level_meter(1, i)
                self.set_level_meter(2, i)
                if i > 64:
                    for pad in range(8):
                        self.set_pad(1, pad, LEDState.ON, mode='HOT_CUE')
                        self.set_pad(2, pad, LEDState.ON, mode='HOT_CUE')
                time.sleep(0.03)

            # Fade out
            for i in range(127, -1, -8):
                self.set_level_meter(1, i)
                self.set_level_meter(2, i)
                if i < 64:
                    for pad in range(8):
                        self.set_pad(1, pad, LEDState.OFF, mode='HOT_CUE')
                        self.set_pad(2, pad, LEDState.OFF, mode='HOT_CUE')
                time.sleep(0.03)

    def _screensaver_chase(self):
        """Chase lights around the controller"""
        print("Effect: Chase")
        for _ in range(4):
            # Deck 1 pads left to right
            for i in range(8):
                self.set_pad(1, i, LEDState.ON, mode='HOT_CUE')
                time.sleep(0.06)
                if i > 0:
                    self.set_pad(1, i-1, LEDState.OFF, mode='HOT_CUE')

            # Deck 2 pads right to left
            for i in range(7, -1, -1):
                self.set_pad(2, i, LEDState.ON, mode='HOT_CUE')
                time.sleep(0.06)
                if i < 7:
                    self.set_pad(2, i+1, LEDState.OFF, mode='HOT_CUE')

            self.set_pad(1, 7, LEDState.OFF, mode='HOT_CUE')
            self.set_pad(2, 0, LEDState.OFF, mode='HOT_CUE')

    def _screensaver_random_pads(self):
        """Random pad twinkling"""
        print("Effect: Twinkle")
        import random
        active_pads = []

        for _ in range(40):
            # Turn on random pad
            deck = random.choice([1, 2])
            pad = random.randint(0, 7)
            self.set_pad(deck, pad, LEDState.ON, mode='HOT_CUE')
            active_pads.append((deck, pad))

            # Turn off oldest if too many are on
            if len(active_pads) > 6:
                old_deck, old_pad = active_pads.pop(0)
                self.set_pad(old_deck, old_pad, LEDState.OFF, mode='HOT_CUE')

            time.sleep(0.1)

        # Clean up remaining
        for deck, pad in active_pads:
            self.set_pad(deck, pad, LEDState.OFF, mode='HOT_CUE')

    def _screensaver_vu_meters(self):
        """Simulated VU meters with music-like patterns"""
        print("Effect: VU Meters")
        import random

        for _ in range(60):
            # Simulate varying levels
            level1 = random.randint(50, 127)
            level2 = random.randint(50, 127)

            self.set_level_meter(1, level1)
            self.set_level_meter(2, level2)

            # Light pads based on level
            num_pads1 = int((level1 / 127) * 8)
            num_pads2 = int((level2 / 127) * 8)

            for i in range(8):
                self.set_pad(1, i, LEDState.ON if i <
                             num_pads1 else LEDState.OFF, mode='HOT_CUE')
                self.set_pad(2, i, LEDState.ON if i <
                             num_pads2 else LEDState.OFF, mode='HOT_CUE')

            time.sleep(0.08)

        # Fade out
        for i in range(127, -1, -10):
            self.set_level_meter(1, i)
            self.set_level_meter(2, i)
            time.sleep(0.02)

    def _screensaver_ping_pong(self):
        """Ping pong effect between decks"""
        print("Effect: Ping Pong")
        for _ in range(3):
            # Deck 1 to Deck 2
            for i in range(8):
                self.set_pad(1, i, LEDState.ON, mode='HOT_CUE')
                self.set_level_meter(1, int((i / 7) * 127))
                time.sleep(0.05)

            time.sleep(0.1)

            for i in range(8):
                self.set_pad(1, i, LEDState.OFF, mode='HOT_CUE')
                self.set_pad(2, i, LEDState.ON, mode='HOT_CUE')
                self.set_level_meter(1, int((1 - i / 7) * 127))
                self.set_level_meter(2, int((i / 7) * 127))
                time.sleep(0.05)

            time.sleep(0.1)

            # Deck 2 back to Deck 1
            for i in range(7, -1, -1):
                self.set_pad(2, i, LEDState.OFF, mode='HOT_CUE')
                self.set_level_meter(2, int((i / 7) * 127))
                time.sleep(0.05)

            self.set_level_meter(1, 0)
            self.set_level_meter(2, 0)
            time.sleep(0.1)

    def _screensaver_sparkle(self):
        """Random sparkle effect on all controls"""
        print("Effect: Sparkle")
        import random

        buttons = [
            (1, 'PLAY_PAUSE'), (2, 'PLAY_PAUSE'),
            (1, 'CUE'), (2, 'CUE'),
            (1, 'BEAT_SYNC'), (2, 'BEAT_SYNC'),
        ]

        active_items = []

        for _ in range(50):
            # Random pad
            deck = random.choice([1, 2])
            pad = random.randint(0, 7)
            self.set_pad(deck, pad, LEDState.ON, mode='HOT_CUE')
            active_items.append(('pad', deck, pad))

            # Occasionally light a button
            if random.random() > 0.7:
                deck, button = random.choice(buttons)
                self.set_deck_button(deck, button, LEDState.ON)
                active_items.append(('button', deck, button))

            # Turn off oldest items
            if len(active_items) > 10:
                item_type, *args = active_items.pop(0)
                if item_type == 'pad':
                    deck, pad = args
                    self.set_pad(deck, pad, LEDState.OFF, mode='HOT_CUE')
                else:
                    deck, button = args
                    self.set_deck_button(deck, button, LEDState.OFF)

            time.sleep(0.08)

        # Clean up
        for item in active_items:
            item_type, *args = item
            if item_type == 'pad':
                deck, pad = args
                self.set_pad(deck, pad, LEDState.OFF, mode='HOT_CUE')
            else:
                deck, button = args
                self.set_deck_button(deck, button, LEDState.OFF)

    def close(self):
        """Close the MIDI output port"""
        self.output.close()


# ==================== Example Usage ====================

if __name__ == "__main__":
    # Initialize controller
    led = FLX4LEDController()

    try:
        # Turn off all LEDs first
        led.all_leds_off()
        time.sleep(0.5)

        print("\n" + "="*50)
        print("DDJ-FLX4 LED Controller Demo")
        print("="*50)

        # Quick test pattern
        print("\n[1/3] Running quick test pattern...")
        led.test_pattern(delay=0.15)
        time.sleep(1)

        # Volume meter demo
        print("\n[2/3] Volume meter demo...")
        print("Animating both meters...")
        for i in range(128):
            led.set_level_meter(1, i)
            led.set_level_meter(2, 127 - i)
            time.sleep(0.01)

        led.set_level_meter(1, 0)
        led.set_level_meter(2, 0)
        time.sleep(0.5)

        # Screensaver demos
        print("\n[3/3] Screensaver Animations Demo")
        print("="*50)
        print("Press Ctrl+C at any time to skip to next animation\n")

        screensavers = [
            ("Breathing", lambda: led.screensaver_breathing(15, 2.0)),
            ("Knight Rider", lambda: led.screensaver_knight_rider(15, 0.05)),
            ("Wave", lambda: led.screensaver_wave(15, 0.05)),
            ("Rainbow Chase", lambda: led.screensaver_rainbow_chase(15, 0.08)),
            ("Random Pads", lambda: led.screensaver_random_pads(15, 0.1)),
            ("Pulse Buttons", lambda: led.screensaver_pulse_buttons(15, 0.5)),
        ]

        for name, screensaver in screensavers:
            try:
                print(f"\n▶ {name} (15 seconds)...")
                screensaver()
                time.sleep(1)
            except KeyboardInterrupt:
                print(f"  Skipped!")
                led.all_leds_off()
                time.sleep(0.5)

        # Infinite screensaver mode
        print("\n" + "="*50)
        print("SCREENSAVER MODE (Random Mix)")
        print("="*50)
        print("Running infinite screensaver with random animations.")
        print("Press Ctrl+C to exit.\n")

        # This will run forever until Ctrl+C
        led.screensaver_random_mix(duration=float('inf'))

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        print("\nCleaning up...")
        led.all_leds_off()
        led.close()
        print("Done! 👋")

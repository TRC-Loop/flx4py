import mido
from threading import Thread


class FLX4:
    # PAD mapping: note → index (0-7)
    PAD_MAP = {
        7: {48: 0, 49: 1, 50: 2, 51: 3, 52: 4, 53: 5, 54: 6, 55: 7},  # DECK 1
        9: {48: 0, 49: 1, 50: 2, 51: 3, 52: 4, 53: 5, 54: 6, 55: 7},  # DECK 2
    }

    # TAB keys mapping: note → index (0-3)
    TAB_MAP = {
        0: {27: 0, 30: 1, 32: 2, 34: 3},  # DECK 1 TAB
        1: {27: 0, 30: 1, 32: 2, 34: 3},  # DECK 2 TAB
    }

    # Jogwheel mapping: (channel, control) → name
    JOG_MAP = {
        (0, 34): "DECK 1 JOG TOP",
        (0, 33): "DECK 1 JOG SIDE",
        (1, 34): "DECK 2 JOG TOP",
        (1, 33): "DECK 2 JOG SIDE",
    }

    # Jogwheel touch mapping: note → deck
    JOG_TOUCH = {
        (0, 54): "DECK 1 JOG TOUCH",
        (1, 54): "DECK 2 JOG TOUCH",
    }

    # Button mapping: (channel, note) → name
    BUTTON_MAP = {
        # DECK 1 buttons
        (0, 11): "DECK 1 PLAY/PAUSE",
        (0, 14): "DECK 1 PLAY/PAUSE SHIFT",
        (0, 12): "DECK 1 CUE",
        (0, 72): "DECK 1 CUE SHIFT",
        (0, 84): "DECK 1 CUE/LOOP CALL",  # Manual says 63, actual sends 84
        (0, 16): "DECK 1 IN",
        (0, 76): "DECK 1 IN SHIFT",
        (0, 17): "DECK 1 OUT",
        (0, 78): "DECK 1 OUT SHIFT",
        (0, 77): "DECK 1 4 BEAT/EXIT",
        (0, 80): "DECK 1 4 BEAT/EXIT SHIFT",
        (0, 81): "DECK 1 CUE/LOOP CALL LEFT",
        (0, 62): "DECK 1 CUE/LOOP CALL LEFT SHIFT",
        (0, 83): "DECK 1 CUE/LOOP CALL RIGHT",
        (0, 61): "DECK 1 CUE/LOOP CALL RIGHT SHIFT",
        (0, 88): "DECK 1 BEAT SYNC",
        (0, 92): "DECK 1 BEAT SYNC LONG",
        (0, 96): "DECK 1 BEAT SYNC SHIFT",
        (0, 63): "DECK 1 SHIFT",  # Manual says 84, actual sends 63
        (0, 104): "DECK 1 SHIFT SHIFT",

        # DECK 2 buttons
        (1, 11): "DECK 2 PLAY/PAUSE",
        (1, 14): "DECK 2 PLAY/PAUSE SHIFT",
        (1, 12): "DECK 2 CUE",
        (1, 72): "DECK 2 CUE SHIFT",
        (1, 84): "DECK 2 CUE/LOOP CALL",  # Manual says 63, actual sends 84
        (1, 16): "DECK 2 IN",
        (1, 76): "DECK 2 IN SHIFT",
        (1, 17): "DECK 2 OUT",
        (1, 78): "DECK 2 OUT SHIFT",
        (1, 77): "DECK 2 4 BEAT/EXIT",
        (1, 80): "DECK 2 4 BEAT/EXIT SHIFT",
        (1, 81): "DECK 2 CUE/LOOP CALL LEFT",
        (1, 62): "DECK 2 CUE/LOOP CALL LEFT SHIFT",
        (1, 83): "DECK 2 CUE/LOOP CALL RIGHT",
        (1, 61): "DECK 2 CUE/LOOP CALL RIGHT SHIFT",
        (1, 88): "DECK 2 BEAT SYNC",
        (1, 92): "DECK 2 BEAT SYNC LONG",
        (1, 96): "DECK 2 BEAT SYNC SHIFT",
        (1, 63): "DECK 2 SHIFT",  # Manual says 84, actual sends 63
        (1, 104): "DECK 2 SHIFT SHIFT",

        # EFFECT buttons
        (4, 99): "FX BEAT LEFT",
        (4, 100): "FX BEAT LEFT SHIFT",
        (4, 74): "FX BEAT RIGHT",
        (4, 102): "FX BEAT RIGHT SHIFT",
        (4, 75): "FX ON/OFF",
        (4, 107): "FX ON/OFF SHIFT",
        (4, 71): "FX CH SELECT CH1",
        (5, 71): "FX CH SELECT CH2",
        (4, 67): "FX SELECT CH1",
        (5, 67): "FX SELECT CH2",

        # MIXER buttons
        (6, 99): "MASTER CUE",
        (6, 120): "MASTER CUE SHIFT",
        # Note: CH1 CUE and CH2 CUE are same as DECK CUE/LOOP CALL buttons (same MIDI notes)

        # BROWSE buttons (Note: Actual values differ from manual)
        (6, 70): "BROWSE LOAD DECK 1",  # Manual says 65, actual sends 70
        (6, 66): "BROWSE LOAD DECK 1 SHIFT",
        (6, 71): "BROWSE LOAD DECK 2",  # Manual says 70, actual sends 71
        (6, 104): "BROWSE LOAD DECK 2 SHIFT",
        (6, 65): "BROWSE PRESS",  # Manual says 71, actual sends 65
        (6, 122): "BROWSE PRESS SHIFT",
    }

    # 14-bit control mapping: (channel, MSB_cc) → (name, LSB_cc)
    CONTROL_14BIT = {
        # DECK 1 controls
        # Note: Manual says CC 8/40, but actual device sends CC 0/32
        (0, 0): ("DECK 1 TEMPO", 32),
        (0, 2): ("DECK 1 TRIM", 34),
        (0, 4): ("DECK 1 EQ HI", 36),
        (0, 7): ("DECK 1 EQ MID", 39),
        (0, 11): ("DECK 1 EQ LOW", 43),
        (0, 15): ("DECK 1 CFX", 47),
        (0, 19): ("DECK 1 CH FADER", 51),

        # DECK 2 controls
        # Note: Manual says CC 8/40, but actual device sends CC 0/32
        (1, 0): ("DECK 2 TEMPO", 32),
        (1, 2): ("DECK 2 TRIM", 34),
        (1, 4): ("DECK 2 EQ HI", 36),
        (1, 7): ("DECK 2 EQ MID", 39),
        (1, 11): ("DECK 2 EQ LOW", 43),
        (1, 15): ("DECK 2 CFX", 47),
        (1, 19): ("DECK 2 CH FADER", 51),

        # FX controls
        (4, 2): ("FX LEVEL/DEPTH", 34),

        # MIXER controls
        (6, 5): ("MASTER LEVEL", 37),
        (6, 12): ("HEADPHONE MIX", 44),
        (6, 13): ("HEADPHONE LEVEL", 45),
        (6, 23): ("MIC LEVEL", 55),
        (6, 24): ("SMART FADER", 56),
        (6, 31): ("CROSSFADER", 63),
    }

    # Single-byte CC controls
    CONTROL_7BIT = {
        (6, 64): "BROWSE ROTATE",
        (6, 100): "BROWSE ROTATE SHIFT",
    }

    # Slider for Android MONO/STEREO
    SLIDER_MAP = {
        (6, 109): "ANDROID MONO/STEREO",
    }

    def __init__(self, name_keyword: str = "FLX4"):
        self.name = self.find_device(name_keyword)
        if not self.name:
            raise RuntimeError("FLX4 not found")
        self.input = mido.open_input(self.name)
        self.running = False

        # Storage for 14-bit values (MSB/LSB pairs)
        self.control_values = {}

    @staticmethod
    def find_device(keyword: str) -> str | None:
        for name in mido.get_input_names():
            if keyword in name:
                return name
        return None

    def _combine_14bit(self, msb: int, lsb: int) -> int:
        """Combine MSB and LSB into 14-bit value (0-16383)"""
        return (msb << 7) | lsb

    def _normalize_14bit(self, value: int) -> float:
        """Normalize 14-bit value to 0.0-1.0"""
        return value / 16383.0

    def _tempo_to_range(self, value: int) -> float:
        """Convert 14-bit tempo value to -1.0 to +1.0 range (centered at 0)"""
        # Center is at 8192 (0x2000)
        normalized = (value - 8192) / 8192.0
        return max(-1.0, min(1.0, normalized))

    def _process_14bit_control(self, channel: int, control: int, value: int):
        """Process MSB or LSB of a 14-bit control"""
        key = (channel, control)

        # Check if this is an MSB
        if key in self.CONTROL_14BIT:
            name, lsb_cc = self.CONTROL_14BIT[key]
            control_key = f"{channel}_{name}"

            # Store MSB
            if control_key not in self.control_values:
                self.control_values[control_key] = {'msb': 0, 'lsb': 0}
            self.control_values[control_key]['msb'] = value

            # Combine and output
            combined = self._combine_14bit(
                self.control_values[control_key]['msb'],
                self.control_values[control_key]['lsb']
            )

            # Special handling for TEMPO (centered) vs others (0-1)
            if "TEMPO" in name:
                normalized = self._tempo_to_range(combined)
                print(f"{name} = {normalized:.3f} (raw: {combined})")
            else:
                normalized = self._normalize_14bit(combined)
                print(f"{name} = {normalized:.3f} (raw: {combined})")

        else:
            # Check if this is an LSB
            for (ch, msb_cc), (name, lsb_cc) in self.CONTROL_14BIT.items():
                if ch == channel and lsb_cc == control:
                    control_key = f"{channel}_{name}"

                    # Store LSB
                    if control_key not in self.control_values:
                        self.control_values[control_key] = {'msb': 0, 'lsb': 0}
                    self.control_values[control_key]['lsb'] = value

                    # Combine and output
                    combined = self._combine_14bit(
                        self.control_values[control_key]['msb'],
                        self.control_values[control_key]['lsb']
                    )

                    # Special handling for TEMPO (centered) vs others (0-1)
                    if "TEMPO" in name:
                        normalized = self._tempo_to_range(combined)
                        print(f"{name} = {normalized:.3f} (raw: {combined})")
                    else:
                        normalized = self._normalize_14bit(combined)
                        print(f"{name} = {normalized:.3f} (raw: {combined})")
                    return

    def start_listening(self):
        if self.running:
            return
        self.running = True

        def loop():
            while self.running:
                for msg in self.input.iter_pending():
                    # PADs, TABs, JOG TOUCH, and other buttons
                    if msg.type == 'note_on':
                        state = "pressed" if msg.velocity > 0 else "released"

                        # PADs
                        if msg.channel in self.PAD_MAP and msg.note in self.PAD_MAP[msg.channel]:
                            index = self.PAD_MAP[msg.channel][msg.note]
                            deck_num = 1 if msg.channel == 7 else 2
                            print(f"DECK {deck_num} PAD {index} ({state})")

                        # TAB keys
                        elif msg.channel in self.TAB_MAP and msg.note in self.TAB_MAP[msg.channel]:
                            index = self.TAB_MAP[msg.channel][msg.note]
                            deck_num = 1 if msg.channel == 0 else 2
                            print(f"DECK {deck_num} TAB {index} ({state})")

                        # Jogwheel touch
                        elif (msg.channel, msg.note) in self.JOG_TOUCH:
                            print(
                                f"{self.JOG_TOUCH[(msg.channel, msg.note)]} ({state})")

                        # Other buttons
                        elif (msg.channel, msg.note) in self.BUTTON_MAP:
                            button_name = self.BUTTON_MAP[(
                                msg.channel, msg.note)]
                            print(f"{button_name} ({state})")

                        # Anything else
                        else:
                            print(f"UNMAPPED NOTE: ch={msg.channel} note={
                                  msg.note} vel={msg.velocity}")

                    # Jogwheel rotation, knobs, and faders
                    elif msg.type == 'control_change':
                        # Check for jogwheel first (they use relative values)
                        jog_name = self.JOG_MAP.get((msg.channel, msg.control))
                        if jog_name:
                            if msg.value == 63:
                                direction = "LEFT"
                            elif msg.value == 65:
                                direction = "RIGHT"
                            else:
                                direction = f"VALUE {msg.value}"
                            print(f"{jog_name} TURN {direction}")

                        # Check for 14-bit controls
                        elif (msg.channel, msg.control) in self.CONTROL_14BIT or \
                            any(lsb == msg.control and ch == msg.channel
                                for (ch, _), (_, lsb) in self.CONTROL_14BIT.items()):
                            self._process_14bit_control(
                                msg.channel, msg.control, msg.value)

                        # Check for 7-bit controls
                        elif (msg.channel, msg.control) in self.CONTROL_7BIT:
                            control_name = self.CONTROL_7BIT[(
                                msg.channel, msg.control)]
                            # Browse encoder uses relative encoding
                            if "BROWSE ROTATE" in control_name:
                                if msg.value >= 0x01 and msg.value <= 0x40:
                                    direction = f"RIGHT {msg.value}"
                                else:
                                    direction = f"LEFT {128 - msg.value}"
                                print(f"{control_name} {direction}")
                            else:
                                print(f"{control_name} = {msg.value}")

                        # Check for slider
                        elif (msg.channel, msg.control) in self.SLIDER_MAP:
                            slider_name = self.SLIDER_MAP[(
                                msg.channel, msg.control)]
                            mode = "STEREO" if msg.value == 0 else "MONO"
                            print(f"{slider_name} = {mode}")

                        else:
                            print(f"UNMAPPED CC: ch={msg.channel} cc={
                                  msg.control} val={msg.value}")

                    else:
                        print(f"OTHER MESSAGE: {msg}")

        self.thread = Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.input.close()

    def get_control_value(self, control_name: str, deck: int = None) -> float | None:
        """
        Get the current normalized value of a control.

        Args:
            control_name: Name of control (e.g., "TEMPO", "EQ LOW", "CH FADER", "CROSSFADER")
            deck: Deck number (1 or 2) for deck-specific controls, None for global controls

        Returns:
            Normalized value (0.0-1.0 for most, -1.0 to 1.0 for TEMPO) or None if not found
        """
        if deck:
            full_name = f"DECK {deck} {control_name}"
            channel = deck - 1
        else:
            full_name = control_name
            channel = 6  # Default to mixer channel for global controls

        control_key = f"{channel}_{full_name}"

        if control_key in self.control_values:
            combined = self._combine_14bit(
                self.control_values[control_key]['msb'],
                self.control_values[control_key]['lsb']
            )

            if "TEMPO" in full_name:
                return self._tempo_to_range(combined)
            else:
                return self._normalize_14bit(combined)

        return None


# Example usage
if __name__ == "__main__":
    flx = FLX4()
    flx.start_listening()
    print("Listening for all DDJ-FLX4 controls. Press Ctrl+C to stop.")
    print("\nControls now show normalized values:")
    print("  - TEMPO: -1.0 (slowest) to +1.0 (fastest), 0.0 = center")
    print("  - All other knobs/faders: 0.0 (min) to 1.0 (max)")
    print("  - Raw 14-bit values also shown in parentheses\n")

    import time
    try:
        while True:
            time.sleep(1)

            # Example: Query current tempo value for Deck 1
            # tempo = flx.get_control_value("TEMPO", deck=1)
            # if tempo is not None:
            #     print(f"Current Deck 1 Tempo: {tempo:.3f}")

    except KeyboardInterrupt:
        flx.stop()
        print("\nStopped.")

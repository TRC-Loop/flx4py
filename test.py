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

    def __init__(self, name_keyword: str = "FLX4"):
        self.name = self.find_device(name_keyword)
        if not self.name:
            raise RuntimeError("FLX4 not found")
        self.input = mido.open_input(self.name)
        self.running = False

    @staticmethod
    def find_device(keyword: str) -> str | None:
        for name in mido.get_input_names():
            if keyword in name:
                return name
        return None

    def start_listening(self):
        if self.running:
            return
        self.running = True

        def loop():
            while self.running:
                for msg in self.input.iter_pending():
                    # PADs, TABs, JOG TOUCH
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

                        # Anything else
                        else:
                            print(f"UNMAPPED NOTE: {msg}")

                    # Jogwheel rotation
                    elif msg.type == 'control_change':
                        jog_name = self.JOG_MAP.get((msg.channel, msg.control))
                        if jog_name:
                            if msg.value == 63:
                                direction = "LEFT"
                            elif msg.value == 65:
                                direction = "RIGHT"
                            else:
                                direction = f"VALUE {msg.value}"
                            print(f"{jog_name} TURN {direction}")
                        else:
                            print(f"CONTROL CHANGE: {msg}")

                    else:
                        print(f"OTHER MESSAGE: {msg}")

        self.thread = Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.input.close()


# Example usage
if __name__ == "__main__":
    flx = FLX4()
    flx.start_listening()
    print("Listening for PADs, TAB keys, JOG rotation, and JOG touch. Press Ctrl+C to stop.")

    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        flx.stop()
        print("Stopped.")

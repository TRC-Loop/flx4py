import mido
from typing import List


class MidiDeviceManager:
    @staticmethod
    def get_input_devices() -> List[str]:
        return mido.get_input_names()

    @staticmethod
    def get_output_devices() -> List[str]:
        return mido.get_output_names()

    @staticmethod
    def print_devices() -> None:
        inputs = MidiDeviceManager.get_input_devices()
        outputs = MidiDeviceManager.get_output_devices()

        print("MIDI Input Devices:")
        for device in inputs:
            print(f"  - {device}")

        print("\nMIDI Output Devices:")
        for device in outputs:
            print(f"  - {device}")


if __name__ == "__main__":
    MidiDeviceManager.print_devices()

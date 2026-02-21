"""
System volume control via DDJ-FLX4 channel fader.

Deck 1 CH FADER → system output volume (macOS).
The VU meters mirror the current volume level in real time.

Run with:  python examples/volume_control.py
Stop with: Ctrl+C
"""

import subprocess
import time
import threading
import flx4py


def get_volume() -> float:
    result = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True, text=True,
    )
    return int(result.stdout.strip()) / 100.0


def set_volume(level: float) -> None:
    level = max(0.0, min(1.0, level))
    subprocess.run(
        ["osascript", "-e", f"set volume output volume {int(level * 100)}"],
        check=False,
    )


controller = flx4py.DDJFlx4()
_last_fader: float | None = None


@controller.on_knob("CH_FADER", deck=1)
def fader_moved(event: flx4py.KnobEvent) -> None:
    global _last_fader
    _last_fader = event.value
    set_volume(event.value)


def meter_update_loop() -> None:
    while True:
        vol = get_volume()
        controller.leds.set_level_meter(1, vol)
        controller.leds.set_level_meter(2, vol)
        time.sleep(0.05)


with controller:
    print("Deck 1 CH FADER → system volume. Press Ctrl+C to quit.")
    threading.Thread(target=meter_update_loop, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.leds.all_off()
        print("Stopped.")

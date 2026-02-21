"""
Cross-platform system volume control via DDJ-FLX4 channel fader.

Deck 1 CH FADER  →  system output volume
VU meters        ←  mirror current volume level

Platform notes
--------------
macOS   : uses osascript  (built-in, no extra packages)
Linux   : uses pactl      (PulseAudio; install: apt install pulseaudio-utils)
Windows : uses pycaw      (install: pip install pycaw comtypes)

Run with:  python examples/volume_control.py
Stop with: Ctrl+C
"""

import re
import subprocess
import sys
import threading
import time

import flx4py


# ---------------------------------------------------------------------------
# Cross-platform volume helpers
# ---------------------------------------------------------------------------

def _get_volume_macos() -> float:
    r = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True, text=True,
    )
    return int(r.stdout.strip()) / 100.0


def _set_volume_macos(level: float) -> None:
    subprocess.run(
        ["osascript", "-e", f"set volume output volume {int(level * 100)}"],
        check=False,
    )


def _get_volume_linux() -> float:
    r = subprocess.run(
        ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
        capture_output=True, text=True,
    )
    m = re.search(r"(\d+)%", r.stdout)
    return int(m.group(1)) / 100.0 if m else 0.5


def _set_volume_linux(level: float) -> None:
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{int(level * 100)}%"],
        check=False,
    )


def _get_volume_windows() -> float:
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL  # type: ignore[import]
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore[import]
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return float(volume.GetMasterVolumeLevelScalar())
    except ImportError:
        raise RuntimeError(
            "pycaw is required on Windows: pip install pycaw comtypes"
        )


def _set_volume_windows(level: float) -> None:
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL  # type: ignore[import]
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore[import]
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level, None)
    except ImportError:
        raise RuntimeError(
            "pycaw is required on Windows: pip install pycaw comtypes"
        )


if sys.platform == "darwin":
    get_volume = _get_volume_macos
    set_volume = _set_volume_macos
elif sys.platform == "win32":
    get_volume = _get_volume_windows
    set_volume = _set_volume_windows
else:
    get_volume = _get_volume_linux
    set_volume = _set_volume_linux


# ---------------------------------------------------------------------------
# Controller setup
# ---------------------------------------------------------------------------

controller = flx4py.DDJFlx4()


@controller.on_knob("CH_FADER", deck=1)
def fader_moved(event: flx4py.KnobEvent) -> None:
    set_volume(event.value)


def meter_loop() -> None:
    while True:
        vol = get_volume()
        controller.leds.set_level_meter(1, vol)
        controller.leds.set_level_meter(2, vol)
        time.sleep(0.05)


with controller:
    print(f"[flx4py] Deck 1 CH FADER → system volume  ({sys.platform})")
    print("[flx4py] Press Ctrl+C to quit.")
    threading.Thread(target=meter_loop, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.leds.all_off()
        print("\n[flx4py] Stopped.")

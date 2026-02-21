# Animations

`LEDController` includes several built-in animations that run for a fixed duration and then turn all LEDs off. They are blocking — run them in a thread if you need your main loop to stay responsive.

All animations are accessed via `controller.leds`.

## Available animations

### Wave

A single lit pad sweeps across both decks continuously.

```python
controller.leds.animate_wave(duration=10.0, speed=0.06)
```

### Knight Rider

A single lit pad bounces left and right while the VU meters follow.

```python
controller.leds.animate_knight_rider(duration=10.0, speed=0.05)
```

### Breathing

Pads and VU meters pulse together in a slow breathing pattern.

```python
controller.leds.animate_breathing(duration=10.0, cycle=2.0)
```

`cycle` is the duration of one full inhale/exhale cycle in seconds.

### Ping Pong

A lit pad travels from deck 1 across to deck 2 and back.

```python
controller.leds.animate_ping_pong(duration=10.0, speed=0.05)
```

### Sparkle

Random pads and buttons twinkle on and off independently.

```python
controller.leds.animate_sparkle(duration=10.0, speed=0.08)
```

### Rainbow Chase

A moving group of lit pads chases across both decks while the VU meters play a counter-phase pattern.

```python
controller.leds.animate_rainbow_chase(duration=10.0, speed=0.08)
```

## Running animations in a background thread

Because animation methods block until `duration` expires, run them in a `threading.Thread` if you still need your callbacks to fire:

```python
import threading

def run_animation():
    controller.leds.animate_breathing(duration=30.0)

t = threading.Thread(target=run_animation, daemon=True)
t.start()
```

## Building your own

All LED methods are synchronous and thread-safe, so you can compose your own animations easily:

```python
import time

def my_animation(duration: float = 10.0):
    end = time.monotonic() + duration
    pos = 0
    while time.monotonic() < end:
        for deck in (1, 2):
            for i in range(8):
                controller.leds.set_pad(deck, i, i == pos % 8)
        controller.leds.set_level_meter(1, (pos % 8) / 7)
        controller.leds.set_level_meter(2, 1.0 - (pos % 8) / 7)
        pos += 1
        time.sleep(0.07)
    controller.leds.all_off()
```

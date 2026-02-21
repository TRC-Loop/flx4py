# Installation

## Requirements

- **Python 3.10 or newer**
- **Pioneer DDJ-FLX4** connected via USB
- The device should appear automatically as a MIDI device — no additional drivers are needed on macOS or Linux. On Windows, install the [official Pioneer DJ driver](https://www.pioneerdj.com/en/support/software/ddj-flx4/).

## Install from PyPI

```bash
pip install flx4py
```

## Install from source

```bash
git clone https://github.com/TRC-Loop/flx4py.git
cd flx4py
pip install .
```

## Verify the connection

After plugging in your controller, you can list available MIDI devices:

```python
import mido
print(mido.get_input_names())
print(mido.get_output_names())
```

You should see entries containing `FLX4`. If nothing appears, try a different USB cable or port.

## Install docs dependencies

If you want to build the documentation locally:

```bash
pip install "flx4py[docs]"
mkdocs serve
```

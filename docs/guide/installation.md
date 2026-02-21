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

## Build the documentation locally

Install the docs group first, then serve:

```bash
# With poetry (recommended)
poetry install --with docs
poetry run mkdocs serve

# With pip
pip install "flx4py[docs]"
mkdocs serve
```

!!! warning "MkDocs version"
    flx4py's documentation requires **MkDocs 1.x** (pinned `<2.0.0`).
    MkDocs 2.0 is not compatible with the Material theme used here.

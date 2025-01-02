# Traffic lights portable

## Setup

Create a virtualenv with
```
python -m venv venv
source venv/bin/active
pip install -r requirements.txt
```

Set led strips DIN to GPIO21, GND to RPi GND and 5V to RPi 5v

For USB speakers set /etc/asound.conf
to

defaults.pcm.card 1
defaults.ctl.card 1

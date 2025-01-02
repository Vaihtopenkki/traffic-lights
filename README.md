# Traffic lights portable

## Setup

Create a virtualenv with 
```
python -m venv venv
source venv/bin/active
pip install -r requirements.txt
```
Disable audio output from Raspberry Pi to GPIO pins
in /boot/firmware/config.txt find `dtparam=audio=on` and set it to `dtparam=audio=off`

Set led strips DIN to GPIO21, GND to RPi GND and 5V to RPi 5v

# InkyKeys
### Type using nothing but your MacBook's touchpad
(WARNING: Completely useless!)

## Requirements
* MacBook model with haptic touchpad
* Raspberry Pi >=4 / Zero W / other device which supports USB OTG
* USB-C cable
* Local network for both MacBook and Raspberry Pi

## Installation / Usage
On both devices:
* `git clone https://github.com/Capta1nT0ad/InkyKeys`
* `cd InkyKeys`

On MacBook:
* `cd client`
* `nano .env` >> add API_KEY=your_gemini_api_key and KEYSTROKE_SERVER=https://raspberrypi:8000 or similar
* `pip install -r requirements.txt`
* `python3 main.py`

On Raspberry Pi or similar:
* `cd server`
* `bash enable-usb-hid.sh`
* `sudo reboot`
* `pip install -r requirements.txt`
* `python3 main.py`

If successful, open a text document and try writing on the MacBook touchpad. After 0.5 seconds of inactivity, the word will be sent off to the AI model and 1-2 seconds later it will return and be written.

* Drawing a line across the very bottom edge of the touchpad will add a space. 
* Drawing a diagonal line from one corner to the other will backspace.
* Drawing a line across the very right or left edge of the touchpad will add a return.

## Recommended Models
* gemini-2.0-flash-lite offers 30 requests per minute at 200 requests per day.
* gemini-2.5-flash-lite offers 15 requests per minute at 1000 requests per day.

## Credits

* Michael Lynch's Key Mime Pi for providing the Pi's HID code >> [https://mtlynch.io/key-mime-pi/](https://mtlynch.io/key-mime-pi/)
* Krish Shah's OpenMultitouchSupport framework >> [https://github.com/KrishKrosh/OpenMultitouchSupport](https://github.com/KrishKrosh/OpenMultitouchSupport)
* Krish Shah's TrackWeight app for the inspiration >> [https://github.com/KrishKrosh/TrackWeight](https://github.com/KrishKrosh/TrackWeight)

import socketio
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    datefmt="%d/%m/%y %H:%M:%S",
    format="%(asctime)s (%(filename)s) [%(levelname)s]: %(message)s",
    force=True
)

punctuation_js_keycodes = {
    '.': (190, False),
    ',': (188, False),
    '/': (191, False),
    '?': (191, True),
    '!': (49, True),
    '@': (50, True),
    '#': (51, True),
    '$': (52, True),
    '%': (53, True),
    '^': (54, True),
    '&': (55, True),
    '*': (56, True),
    '(': (57, True),
    ')': (48, True),
    '-': (189, False),
    '_': (189, True),
    '=': (187, False),
    '+': (187, True),
    ';': (186, False),
    ':': (186, True),
    '\'': (222, False),
    '"': (222, True),
    '[': (219, False),
    '{': (219, True),
    ']': (221, False),
    '}': (221, True),
    '\\': (220, False),
    '|': (220, True),
    '`': (192, False),
    '~': (192, True),
}

SPECIAL_KEYS = {
    '!RETURN!': (13, False),
    '!BACKSPACE!': (8, False),
}

sio = socketio.Client()

def setup_socketio(server):
    if not sio.connected:
        sio.connect(server)

def send_string(text, server):

    logging.debug("Sending text '%s' to server: %s", text, server)

    setup_socketio(server)

    if text in SPECIAL_KEYS:
        key_code, shift = SPECIAL_KEYS[text]
        logging.debug("Found special token '%s' >> keycode %s", text, key_code)
        keystroke_data = {
            'metaKey': False,
            'altKey': False,
            'shiftKey': shift,
            'ctrlKey': False,
            'key': text,
            'keyCode': key_code,
            'location': None,
        }
        logging.debug("Sending: %s", str(keystroke_data))
        sio.emit('keystroke', keystroke_data)
        time.sleep(0.02)
        
        return

    for char in text:
        if char in punctuation_js_keycodes:
            key_code, shift_key = punctuation_js_keycodes[char]
            logging.debug("Found punctuation token '%s' >> keycode %s", char, key_code)
        else:
            key_code = ord(char.upper())
            shift_key = char.isupper()

        keystroke_data = {
            'metaKey': False,
            'altKey': False,
            'shiftKey': shift_key,
            'ctrlKey': False,
            'key': char,
            'keyCode': key_code,
            'location': None,
        }
        logging.debug("Sending: %s", str(keystroke_data))
        sio.emit('keystroke', keystroke_data)
        time.sleep(0.02)
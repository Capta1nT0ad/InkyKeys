import socketio
import time

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

def send_string(text, server):
    sio = socketio.Client()
    sio.connect(server)

    i = 0
    while i < len(text):
        for token, (key_code, shift) in SPECIAL_KEYS.items():
            token_len = len(token)
            if text[i:i+token_len] == token:
                keystroke_data = {
                    'metaKey': False,
                    'altKey': False,
                    'shiftKey': shift,
                    'ctrlKey': False,
                    'key': token,
                    'keyCode': key_code,
                    'location': None,
                }
                sio.emit('keystroke', keystroke_data)
                time.sleep(0.02)
                i += token_len
                break
        else:
            char = text[i]
            if char in punctuation_js_keycodes:
                key_code, shift_key = punctuation_js_keycodes[char]
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
            sio.emit('keystroke', keystroke_data)
            time.sleep(0.02)
            i += 1
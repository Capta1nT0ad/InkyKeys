from setuptools import setup

APP = ['main.py']
DATA_FILES = ['swift/read', 'swift/OpenMultitouchSupportXCF.framework']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PIL', 'pydantic', 'dotenv', 'socketio', 'websocket', 'mac_notifications'],
    'includes': ['google'],
    'iconfile': 'icon.icns'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

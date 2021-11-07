#! /usr/bin/python3
activate_this = '/home/rein/cat-weight/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/rein/cat-weight/')
from catweight import app as application
application.secret_key = 'torontoapikey'

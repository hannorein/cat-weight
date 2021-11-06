#! /usr/bin/python3
import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/rein/cat-weight/')
from cat-weight import app as application
application.secret_key = 'she is too heavy'

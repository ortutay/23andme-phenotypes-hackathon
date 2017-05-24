import os

from config.gunicorn import *

reload = True
preload_app = False
workers = 1

_dir_path = os.path.dirname(os.path.realpath(__file__))
keyfile = _dir_path + '/localhost.key'
certfile = _dir_path + '/localhost.crt'

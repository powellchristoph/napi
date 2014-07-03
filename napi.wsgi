import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.append('/var/www/napi/')

import bottle
from napi import app

application = app
#application = bottle.default_app()

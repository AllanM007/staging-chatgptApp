#!/usr/bin/python
import sys
activate_this = '/var/www/chatgptApp/venv/bin/activate_this.py'
# exec(compile(open(activate_this, "rb").read(), activate_this, 'exec'))
with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec(code, dict(__file__=activate_this))
sys.path.insert(0,'/var/www/chatgptApp/')
from app import app as application

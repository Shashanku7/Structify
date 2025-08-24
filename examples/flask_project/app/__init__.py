from flask import Flask

app = Flask(__name__)

from . import routes  # relative import to avoid warnings
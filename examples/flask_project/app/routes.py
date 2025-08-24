from . import app
from flask import render_template

@app.route("/")
def home():
    return "Hello from Flask Example Project!"
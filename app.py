from flask import Flask
from actions import bp as actionsbp

app = Flask(__name__)

app.secret_key = 'SECRET_KEY'

app.register_blueprint(actionsbp)
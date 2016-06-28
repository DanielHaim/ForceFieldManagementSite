import os
from config import basedir
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask.ext.login import LoginManager
from config import basedir
from flask_wtf.csrf import CsrfProtect
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
ma = Marshmallow(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'signIn'
CsrfProtect(app)
mail = Mail(app)
# Now tell Flask to use the custom class
from .undo_redo import CustomJSONEncoder
app.json_encoder = CustomJSONEncoder
from app import views , models
import quart.flask_patch
from quart import Quart, request, render_template, jsonify, flash, url_for, redirect
import config, os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Quart(__name__)
app.config.from_object(config.Config)

@app.route('/')
async def index():
    return await render_template('index.html')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app.routes import Checker, Login
app.register_blueprint(Checker.CheckerBlueprint)
app.register_blueprint(Login.LoginBlueprint)
from app import models
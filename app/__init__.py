# To use flask commands, uncomment flask import, change Quart to Flask
# and comment all blueprint registration, also comment below line.
import quart.flask_patch
from quart import Quart, render_template
from flask import Flask
import config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

#app = Flask(__name__)
app = Quart(__name__)
app.config.from_object(config.Config)


@app.route('/')
async def index():
    return await render_template('index.html')

@app.errorhandler(401)
async def forbidden():
    return await render_template('forbidden.html')

@app.errorhandler(404)
async def forbidden():
    return await render_template('notfound.html')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login.user_login'

from app.routes import Checker, Login, Task
app.register_blueprint(Checker.CheckerBlueprint)
app.register_blueprint(Login.LoginBlueprint)
app.register_blueprint(Task.TaskBlueprint)
from app import models, helper
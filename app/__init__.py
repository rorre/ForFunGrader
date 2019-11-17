# To use flask commands, uncomment flask import, change Quart to Flask
# and comment all blueprint registration, also comment below line.
import quart.flask_patch
from quart import Quart, render_template
from flask import Flask
import config
import asyncio

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_misaka import Misaka
from aiosmtplib import SMTP, errors
import traceback

#app = Flask(__name__)
app = Quart(__name__, static_url_path='', static_folder='static')
app.config.from_object(config.Config)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.errorhandler(401)
async def forbidden(error):
    return await render_template('forbidden.html')

@app.errorhandler(404)
async def notfound(error):
    return await render_template('notfound.html')

async def keep_alive():
    while not app.smtp.is_connected:
        await app.smtp.connect()
        await app.smtp.ehlo()
        await app.smtp.login(app.config.get('SMTP_USERNAME'), app.config.get('SMTP_PASSWORD'))

@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    try:
        app.smtp = SMTP(hostname=app.config.get('SMTP_SERVER_URL'), start_tls=True, loop=loop)
        await app.smtp.connect()
        await app.smtp.ehlo()
        await app.smtp.login(app.config.get('SMTP_USERNAME'), app.config.get('SMTP_PASSWORD'))
        app.smtp_cron = asyncio.create_task(keep_alive())
    except errors.SMTPAuthenticationError as e:
        app.smtp = None
        print("Cannot seem to be able to connect.")
        print("Mail verification will not work.")
        print(e.message)
    except:
        app.smtp = None
        traceback.print_exc()
        print("An error occured while trying to connect to SMTP server.")
        print("Mail verification will not work.")
    

@app.after_serving
async def shutdown():
    if app.smtp:
        app.smtp.close()
        app.smtp_cron.cancel()

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login.user_login'
misaka =  Misaka(app)

from .routes import Checker, Login, Task, User, Mail
app.register_blueprint(Checker.CheckerBlueprint)
app.register_blueprint(Login.LoginBlueprint)
app.register_blueprint(Task.TaskBlueprint)
app.register_blueprint(User.UserBlueprint)
app.register_blueprint(Mail.MailBlueprint)
from app import models, helper
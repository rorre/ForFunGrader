from app.models import User
from quart import Blueprint, request, redirect, url_for, render_template, flash
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import current_user, login_user, logout_user

LoginBlueprint = Blueprint('login', __name__)

@LoginBlueprint.route('/login', methods=["GET", "POST"])
async def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return await render_template('login.html')

    form = await request.form

    username = form['username']
    password = form['password']

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        await flash("Wrong username/password")
        return redirect(url_for('login.user_login'))

    login_user(user)
    return redirect(url_for('index'))

@LoginBlueprint.route('/register', methods=["GET", "POST"])
async def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return await render_template('register.html')
    
    form = await request.form
    username = form['username']
    password = form['password']
    email = form['email']

    if User.query.filter_by(username=username) or User.query.filter_by(email=email):
        await flash("Username or email already taken.")
        return await render_template('register.html')

    new_user = User(username=username, password_hash=generate_password_hash(password), email=email)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return redirect(url_for('index'))


@LoginBlueprint.route('/logout')
async def logout():
    logout_user()
    return redirect(url_for('index'))
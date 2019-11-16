from app.models import User
from quart import Blueprint, request, redirect, url_for, render_template, flash
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import current_user, login_user, logout_user, login_required

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
    if not user or not user.check_password(password):
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
    username = form.get('username')
    password = form.get('password')
    email = form.get('email')

    if not username or not password or not email:
        await flash("Please input to all forms.")
        return await render_template('register.html')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
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


@LoginBlueprint.route('/changepw', methods=["GET", "POST"])
@login_required
async def change_password():
    if request.method == "GET":
        return await render_template('changepw.html')
    
    form = await request.form
    curpw = form.get('curpassword')
    newpw = form.get('newpassword')

    if not current_user.check_password(curpw):
        await flash("Wrong password.")
        return await render_template('changepw.html')
    
    current_user.set_password(newpw)
    await flash("Done!")
    return redirect(url_for('index'))
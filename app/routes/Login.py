from app.models import User
from quart import Blueprint, request, redirect, url_for, render_template, flash
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import current_user, login_user, logout_user, login_required
from app.helper import get_token

LoginBlueprint = Blueprint('login', __name__)

@LoginBlueprint.route('/login', methods=["GET", "POST"])
async def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return await render_template('login.html')

    form = await request.form

    username = form.get('username')
    password = form.get('password')

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
    username = form.get('username', '').strip()
    password = form.get('password', '').strip()
    first_name = form.get('first', '').strip()
    last_name = form.get('last', '').strip()
    email = form.get('email', '').strip()

    if not all((username, password, email, first_name, last_name)):
        await flash("Please input to all forms.")
        return await render_template('register.html')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        await flash("Username or email already taken.")
        return await render_template('register.html')

    if len(password) < 8:
        await flash("Password must have at least 8 characters.")
        return await render_template('register.html')

    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        email=email,
        first_name=first_name,
        last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    await flash("Registered.")
    return redirect(url_for('mail.send'))


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
    db.session.commit()
    await flash("Done!")
    return redirect(url_for('index'))

@LoginBlueprint.route('/verify', methods=["GET", "POST"])
@login_required
async def verify():
    if request.method == "GET":
        if current_user.verified:
            await flash("You are already verified.")
            return redirect(url_for('index'))
        return await render_template('verify.html')
    
    code = (await request.form).get('code')
    token = get_token(current_user.id)
    if not token:
        await flash('Code timed out.')
        return await render_template('verify.html')
    
    if token != code:
        await flash("Wrong Code.")
        return await render_template('verify.html')
    
    current_user.verified = True
    db.session.commit()
    await flash("Done!")
    return redirect(url_for('index'))
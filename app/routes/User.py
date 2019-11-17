from app.models import User
from quart import Blueprint, request, redirect, url_for, render_template, flash, abort
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash
import os

from flask_login import current_user, login_user, logout_user, login_required

UserBlueprint = Blueprint('user', __name__, static_folder='../static')

@UserBlueprint.route('/user/<username>')
async def show_user(username):
    userdb = User.query.filter_by(username=str(username)).first()
    if not userdb and username.isdigit():
        userdb = User.query.filter_by(id=int(username)).first()
    if not userdb:
        await flash("User not found.")
        abort(404)
    return await render_template('user.html', user=userdb, total_submissions=len(userdb.submissions))

@UserBlueprint.route('/user/<username>/submissions')
async def user_submissions(username):
    userdb = User.query.filter_by(username=str(username)).first()
    if not userdb and username.isdigit():
        userdb = User.query.filter_by(id=int(username)).first()
    if not userdb:
        await flash("User not found.")
        abort(404)
    return await render_template('submissions.html', user=userdb)

@UserBlueprint.route('/avatars/<path:img_path>')
async def user_avatar(img_path):
    if os.path.exists("app/static/avatars/" + img_path):
        return await UserBlueprint.send_static_file('avatars/' + img_path)
    else:
        return await UserBlueprint.send_static_file('avatars/none.png')

@UserBlueprint.route('/settings/me', methods=["GET", "POST"])
@login_required
async def edit_me():
    if request.method == "GET":
        return await render_template('edit_me.html', me=current_user.me)
    
    current_user.me = (await request.form).get('me')
    db.session.commit()
    await flash("Done!")
    return await render_template('edit_me.html', me=current_user.me)

@UserBlueprint.route('/settings/info', methods=["GET", "POST"])
@login_required
async def edit_info():
    if request.method == "GET":
        return await render_template('edit_info.html')
    
    form = await request.form
    first_name = form.get('first')
    last_name = form.get('last')
    email = form.get('email')

    current_user.first_name = first_name or current_user.first_name
    current_user.last_name = last_name or current_user.last_name
    current_user.email = email or current_user.email
    db.session.commit()
    await flash("Done!")
    return await render_template('edit_info.html')

@UserBlueprint.route('/settings', methods=["GET", "POST"])
@login_required
async def settings():
    return await render_template('settings.html')
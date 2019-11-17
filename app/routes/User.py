from app.models import User
from quart import Blueprint, request, redirect, url_for, render_template, flash, abort
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash
import os, html

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
    curme = html.unescape(current_user.me)
    if request.method == "GET":
        return await render_template('edit_me.html', me=curme)
    
    me = (await request.form).get('me', '').strip()
    if not me or len(me) < 5:
        await flash("Please input at least 5 characters.")
        return await render_template('edit_me.html', me=curme)

    current_user.me = html.escape(me)
    db.session.commit()
    await flash("Done!")
    return await render_template('edit_me.html', me=me)

@UserBlueprint.route('/settings/info', methods=["GET", "POST"])
@login_required
async def edit_info():
    if request.method == "GET":
        return await render_template('edit_info.html')
    
    form = await request.form
    first_name = form.get('first')
    last_name = form.get('last')
    email = form.get('email')
    
    if email != current_user.email:
        current_user.verified = False
        redirect = True

    current_user.first_name = first_name or current_user.first_name
    current_user.last_name = last_name or current_user.last_name
    current_user.email = email or current_user.email
    db.session.commit()
    await flash("Done!")
    
    if redirect:
        return redirect(url_for('mail.send'))
    else:
        return await render_template('edit_info.html')

@UserBlueprint.route('/settings', methods=["GET", "POST"])
@login_required
async def settings():
    return await render_template('settings.html')
from app.models import User
from quart import Blueprint, request, redirect, url_for, render_template, flash
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash
from app.helper import send_mail, make_random_str
from flask_login import current_user, login_user, logout_user, login_required

MailBlueprint = Blueprint('mail', __name__)

@MailBlueprint.route('/resend')
@login_required
async def send():
    if current_user.verified:
        await flash("You are already verified.")
        abort(400)
    await send_mail(current_user, make_random_str(6))
    return redirect(url_for('login.verify'))
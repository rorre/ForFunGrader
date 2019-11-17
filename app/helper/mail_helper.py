import asyncio
from app import app
from email.message import EmailMessage

from app.models import User

USER_TOKENS = {}
USER_TASK = {}
async def set_user(id, value):
    USER_TOKENS[id] = value
    await asyncio.sleep(3600)
    USER_TOKENS[id] = ""

async def send_mail(user, code):
    if USER_TASK.get(user.id):
        USER_TASK.get(user.id).cancel()
        USER_TOKENS[user.id] = ""
    USER_TASK[user.id] = asyncio.create_task(set_user(user.id, code))

    message = EmailMessage()
    message["From"] = app.config.get('SMTP_EMAIL')
    message["To"] = user.email
    message["Subject"] = "Grader Verification"
    message.set_content(f"""Hello, {user.username}!
    
This is an automated message to send you a verification code, the code is:
{code}
Please do not reply to this email as it will not be read.""")

    await app.smtp.send_message(message)

def get_token(id):
    return USER_TOKENS.get(id)
from flask.ext.mail import Message
from app import app,mail
from flask import render_template
from config import ADMINS
from threading import Thread
from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject,to,text_body,html_body):
	msg = Message(subject, sender=ADMINS[0], recipients=[to])
	msg.body = text_body 
	msg.html = html_body
	#with app.open_resource("static/img/molecule1.png") as fp:
	#	msg.attach("image.png", "image/png", fp.read())
	send_async_email(app, msg)

def send_confirmation_email(user,confirm_url):
	if (user.email != "danielmoisehaim@gmail.com"):
		return False
	else:
		send_email('Activation account',
				user.email,
				render_template("confirmation_email.txt",user=user,confirm_url=confirm_url),
				render_template("confirmation_email.html",user=user,confirm_url=confirm_url))

				
def send_password_recovery_email(user,passwordRecovery_url):
	if (user.email != "danielmoisehaim@gmail.com"):
		return False
	else:
		send_email('Password recovery',
				user.email,
				'',
				render_template("password_recovery_email.html",user=user,passwordRecovery_url=passwordRecovery_url))

#liens:
#http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support

#https://realpython.com/blog/python/handling-email-confirmation-in-flask/
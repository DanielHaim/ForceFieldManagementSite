from flask.ext.wtf import Form
from wtforms import StringField, BooleanField , PasswordField
from wtforms.validators import DataRequired,Email,EqualTo,Regexp,Length,ValidationError
from flask import g
import re
from .models import *
from app import db

class SignUpForm(Form):
	firstname = StringField('firstname',validators=[DataRequired(message='Firstname required')])
	lastname = StringField('lastname',validators=[DataRequired(message='Lastname required')])
	username = StringField('username')
	email = StringField('email')
	confirmEmail = StringField('confirmEmail',validators=[EqualTo('email',message='Email must match')])
	password = PasswordField('password',validators=[Length(min=5,max=10,message='Password(5-10chars)')])
	confirmPassword = PasswordField('confirmPassword',validators=[EqualTo('password',message='Password must match')])

	def validate_username(form,field):
		if(len(field.data) == 0):
			raise ValidationError('Username required')
		else:
			user = db.session.query(User).filter(User.username == field.data).first()
			if user:
				raise ValidationError('Username existing')
			else:
				return True

	def validate_email(form,field):
		if(len(field.data) == 0):
			raise ValidationError('Email required')
		else:
			#check if is valid email pattern
			email_address = field.data
			match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_address)
			if(match):
				user = db.session.query(User).filter(User.email == field.data).first()
				if user:
					raise ValidationError('Email existing')
				else:
					return True
			else:
				raise ValidationError('Valid Email required')

class SignInForm(Form):
	username = StringField('username',validators=[DataRequired('User Name required')])
	password = PasswordField('password',validators=[DataRequired('Password required')])

class forgotPasswordForm(Form):
	email = StringField('email',validators=[Email(message='Email required')])

class passwordRecoveryForm(Form):
	new_password = PasswordField('new_password',validators=[Length(min=5,max=10,message='Password(5-10chars)')])
	confirm_new_password = PasswordField('confirm_new_password',validators=[EqualTo('new_password',message='Password must match')])

class changePasswordForm(Form):
	old_password = PasswordField('old_password',validators=[DataRequired(message='Password required')])
	new_password = PasswordField('new_password',validators=[Length(min=5,max=10,message='Password(5-10chars)')])
	confirm_new_password = PasswordField('confirm_new_password',validators=[EqualTo('new_password',message='Password must match')])

class userInfoForm(Form):
	firstname = StringField('firstname',validators=[DataRequired(message='Firstname required')])
	lastname = StringField('lastname',validators=[DataRequired(message='Lastname required')])
	username = StringField('username',validators=[DataRequired(message='User Name required')])
	email = StringField('email')

	def validate_email(form,field):
		if(len(field.data) == 0):
			raise ValidationError('Email required')
		else:
			#check if is valid email pattern
			email_address = field.data
			match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_address)
			if(match):
				user = db.session.query(User).filter(User.email == field.data).first()
				if user and  user.user_id != g.user.user_id:
					raise ValidationError('Email existing')
				else:
					return True
			else:
				raise ValidationError('Valid Email required')

class networkUserInfoForm(Form):
	firstname = StringField('firstname',validators=[DataRequired(message='Firstname required')])
	lastname = StringField('lastname',validators=[DataRequired(message='Lastname required')])
	email = StringField('email')

	def validate_email(form,field):
		if(len(field.data) > 0):
			#check if is valid email pattern
			email_address = field.data
			match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_address)
			if(match):
				user = db.session.query(User).filter(User.email == field.data).first()
				if user and user.user_id != g.user.user_id:
					raise ValidationError('Email existing')
				else:
					return True
			else:
				raise ValidationError('Valid Email required')
		else:
			#because email is optional in this form
			return True


class removeAccountForm(Form):
	password = PasswordField('password',validators=[DataRequired('Password required')])

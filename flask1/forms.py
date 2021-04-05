from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from flask1.models import User
# import email_validator as Email

class RegistrationForm(FlaskForm):
	username = StringField('Username',
							validators=[DataRequired(),Length(min=2,max=20)])
	email = StringField('Email',
						validators=[DataRequired(),Email()])
	password = PasswordField('password',
						validators=[DataRequired(),Length(min=8)])
	confirm_pass = PasswordField('Confirm password',
						validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Sign up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username already exists. Please choose another one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email already exists.')

class LoginForm(FlaskForm):

	email = StringField('Email',
						validators=[DataRequired(),Email()])
	password = PasswordField('password',
						validators=[DataRequired(),Length(min=8)])
	remember = BooleanField('Remember me')
	submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
	username = StringField('Username',
	                       validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email',
	                    validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')

	def validate_username(self, username):
	    if username.data != current_user.username:
	        user = User.query.filter_by(username=username.data).first()
	        if user:
	            raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
	    if email.data != current_user.email:
	        user = User.query.filter_by(email=email.data).first()
	        if user:
	            raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
	patient = StringField('Patient', validators=[DataRequired()])
	diagnosis = StringField('Diagnosis', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Post')

class SearchForm(FlaskForm):
	#username = StringField('username', validators=[DataRequired()])
	patient = StringField('Patient', validators=[DataRequired()])
	submit = SubmitField('Search')


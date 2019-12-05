from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField,SubmitField,MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember me', default=False)

class SignupForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class FormatForm(FlaskForm):
    letter = BooleanField(True)
    #scale = BooleanField(True)
    submit = SubmitField(u'Upload')

class EncryptForm(FlaskForm):
    userpassword = StringField('userpassword', validators=[DataRequired()])
    ownerpassword = StringField('ownerpassword', validators=[DataRequired()])
    submit = SubmitField(u'Upload')

class DecryptForm(FlaskForm):
    password = StringField('password', validators=[DataRequired()])
    submit = SubmitField(u'Upload')
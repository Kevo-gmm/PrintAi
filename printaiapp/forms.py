from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, TextAreaField, FileField, SelectField
from wtforms.validators import Length, DataRequired, EqualTo, Email, ValidationError, DataRequired

from printaiapp.models import User


class RegistrationForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username.')
    

    def validate_email_address(self, email_to_check):
        email = User.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError('Email address already exists! Please try a different email address.')

    def validate_phone_number(self, phone_number_to_check):
        phone_number = User.query.filter_by(phone_number=phone_number_to_check.data).first()
        if phone_number:
            raise ValidationError('Phone number already exists! Please try a different phone number.')


    first_name = StringField(label='First name:', validators=[DataRequired()])
    last_name = StringField(label='Last name:', validators=[DataRequired()])
    username = StringField(label='Username:', validators=[Length(min=4,max=30), DataRequired()])
    email = StringField(label='Email:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=7), DataRequired()])
    password2 = PasswordField(label ='Confirm password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create account')


class LoginForm(FlaskForm):
    email = StringField(label='Email:', validators=[DataRequired()])
    password = PasswordField(label='Password:',validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

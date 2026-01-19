from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, PasswordField, FloatField
from wtforms.validators import DataRequired, Email, Length

class RequestForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    service_needed = SelectField('Service Needed', choices=[], validators=[DataRequired()])
    location = StringField('Your Neighborhood', validators=[DataRequired(), Length(min=2, max=100)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Submit Request')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ProviderForm(FlaskForm):
    name = StringField('Provider Name', validators=[DataRequired()])
    service = StringField('Service Type', validators=[DataRequired()])
    location = StringField('Location (Neighborhood)', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=256)])
    phone = StringField('Phone', validators=[DataRequired()])
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    verified = BooleanField('Verified')
    submit = SubmitField('Save Provider')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=5, max=1000)])
    submit = SubmitField('Send Message')

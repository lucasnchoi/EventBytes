#this file is for the forms
#app is the Flask object created in __init__.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField,TextAreaField
from wtforms.validators import DataRequired, Email

class CreateEventForm(FlaskForm):
    eventTypes = ['Academic', 'Arts', 'Athletics', 'Career', 'Cultural', 'Health', 'Social','Music', 'Technology', 'Science', 'Food', 'Environmental', 'Volunteer', 'Travel','Gaming', 'Fashion', 'Fitness', 'Business', 'Literature', 'Film', 'Religious','Other']
    name = StringField('Event Name', validators=[DataRequired()])
    type = SelectField('Event Type', choices=[(type, type) for type in eventTypes], id = "type",validators=[DataRequired()],default='Other')
    time = StringField('Date and Time', validators=[DataRequired()])
    place = StringField('Location', validators=[DataRequired()])
    details = StringField('Description', validators=[DataRequired()])
    booking = StringField('Booking Instructions')
    accommodation = StringField('Accommodation')
    requisite = StringField('Requirements')
    size = StringField('Size')
    contact = TextAreaField('Contact')



class SignupForm(FlaskForm):
    email = StringField('UofT Email Address', validators=[DataRequired(), Email()])
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired()])
    clubRepresentative = SelectField('Are you a club representative?', choices=[('Yes', 'Yes'), ('No', 'No')],id='clubRepresentative', validators=[DataRequired()],default='No')

class RoleForm(FlaskForm):
    roleOptions = ['President', 'Vice President', 'Treasurer', 'Secretary', 'Events Coordinator', 'Social Media Coordinator','Other']
    clubName = StringField('Club Name', id = "clubName",validators=[DataRequired()])
    clubRole = SelectField('Role', choices=[(role, role) for role in roleOptions], id = "clubRole",validators=[DataRequired()],default='Other')


class LoginForm(FlaskForm):
    email = StringField('UofT Email Address', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LogoutForm(FlaskForm):
    submit = SubmitField('Logout')


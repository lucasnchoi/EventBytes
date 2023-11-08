#this file is for the forms
#app is the Flask object created in __init__.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField,TextAreaField,DateTimeLocalField,IntegerField
from wtforms.validators import DataRequired, Email

class CreateEventForm(FlaskForm):
    eventTypes = ['Academic', 'Arts', 'Athletics', 'Career', 'Cultural', 'Health', 'Social','Music', 'Technology', 'Science', 'Food', 'Environmental', 'Volunteer', 'Travel','Gaming', 'Fashion', 'Fitness', 'Business', 'Literature', 'Film', 'Religious','Other']
    name = StringField('Event Name', validators=[DataRequired()], render_kw={"placeholder": 'Add a short and clear name'})
    type = SelectField('Event Type', choices=[(type, type) for type in eventTypes], id = "type",validators=[DataRequired()],default='Other')
    time = DateTimeLocalField('Date and Time', validators=[DataRequired()])
    size = IntegerField('Size', render_kw={"placeholder":'If applicable, provide the maximum number of attendees'})
    location = StringField('Location', validators=[DataRequired()], render_kw={"placeholder":'Where is the event taking place?'})
    details = StringField('Description', validators=[DataRequired()], render_kw={"placeholder":'Tell people more about the event'})
    booking = TextAreaField('Booking Instructions', render_kw={"placeholder":'Should people register via an external link? If so, provide the link here'})
    accommodation = StringField('Accommodation', render_kw={"placeholder":'If applicable, provide accommodation details'})
    requisite = StringField('Requirements', render_kw={"placeholder":'Eg. Bring your own laptop'})
    contact = TextAreaField('Contact', render_kw={"placeholder":'Eg. Email us at : help@mail.com'})
    organizationHosted = SelectField('Are you creating this on behalf of your club?', choices=[('Yes', 'Yes'), ('No', 'No')],id='organizationHosted', validators=[DataRequired()],default='No')

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


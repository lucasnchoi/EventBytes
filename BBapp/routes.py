from flask import Flask, render_template, session, redirect, url_for, flash, Blueprint, request
from datetime import datetime
from  BBapp.forms import *
from BBapp.database import Database
from BBapp.user.user_class import User

db = Database() 

home_page = Blueprint('home_page', __name__, template_folder='templates')
@home_page.route('/')
def home():
    return render_template('index.html', current_time=datetime.utcnow())


create_event_page = Blueprint('create_event_page', __name__, template_folder='templates')
@create_event_page.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = CreateEventForm()

    if session.get('logged_in') != True:
        return redirect(url_for('login_page.login'))
    
    if request.method == 'POST':
        errors = []
        newEvent = {}

        if form.time.data < datetime.now():
            errors.append("Events cannot be created in the past")
        
        if form.size.data < 0:
            errors.append("Attendee size cannot be negative")
            
        
        if (len(errors) > 0):
            return render_template('createEvent.html', form=form, user = session['user'],errors=errors)

        creatingUser = session['user']
        newEvent['name'] = form.name.data
        newEvent['type'] = form.type.data
        newEvent['location'] = form.location.data
        newEvent['time'] = form.time.data
        newEvent['details'] = form.details.data
        newEvent['booking'] = form.booking.data
        newEvent['accommodation'] = form.accommodation.data
        newEvent['requisite'] = form.requisite.data
        newEvent['size'] = form.size.data
        newEvent['contact'] = form.contact.data

        if (creatingUser['orgID'] != 0 and form.organizationHosted.data == 'Yes'): #if user is an org rep and wants to host an event for that organization
            newEvent['organizationId'] = creatingUser['orgID']
        else:
            newEvent['organizationId'] = 0

        newEvent['creatorId'] = session['user']['userID']

        try:
            db.insert_event(newEvent['name'], newEvent['type'], newEvent['location'], newEvent['time'], newEvent['details'], newEvent['booking'], newEvent['accommodation'], newEvent['requisite'], newEvent['size'], newEvent['contact'], newEvent['organizationId'], newEvent['creatorId'])
            return render_template('createEvent.html',  form=form, user = session['user'],errors=[], success=True)
        except Exception as e:
            print(e)
            return render_template('createEvent.html', form=form, user = session['user'],errors=["Failed to create event - {}".format(str(e))], success=False)

 
    return render_template('createEvent.html', form=form, user = session['user'],errors=[],success = None)

signup_page = Blueprint('signup_page', __name__, template_folder='templates')

@signup_page.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    roleForm = RoleForm()

    if request.method == 'POST':
        errors = []
        signupUser = {}  

        if "utoronto" not in form.email.data:
            errors.append("Please use a valid UofT email address")

        if form.password.data != form.confirmPassword.data:
            errors.append("Passwords do not match")

        if form.clubRepresentative.data == 'Yes':
            if not roleForm.clubName.data.strip():
                errors.append("Please enter a club name")

        if (len(errors) > 0):
            return render_template('signup.html', form=form, roleForm=roleForm, errors=errors)

        signupUser['email'] = form.email.data
        signupUser['firstName'] = form.firstName.data
        signupUser['lastName'] = form.lastName.data
        signupUser['phone'] = form.phone.data
        signupUser['password'] = form.password.data

        if form.clubRepresentative.data == 'No':
            signupUser['clubRepresentative'] = False
            signupUser['clubName'] = ""
            signupUser['clubRole'] = ""
            orgId = 0 #default value for no organization
        else:
            signupUser['clubRepresentative'] = True
            signupUser['clubName'] = roleForm.clubName.data
            signupUser['clubRole'] = roleForm.clubRole.data

            '''@Matt todo: get orgID from database given a club name, if it doesn't exist create an org and get the ID
            orgID = db.get_organization(signupUser['clubName'])[0][0]
            if orgID == None:
                #create new org given a club name
                #get generated orgID
            '''
            orgId = 1 #default value for now

        try:
            if db.get_user(signupUser['email']): #if user already exists
                return render_template('signup.html', form=form, roleForm=roleForm, errors=["User with the same email already exists"])
            db.insert_user(signupUser['firstName'],signupUser['lastName'], signupUser['email'], signupUser['phone'], signupUser['password'],orgId, signupUser['clubRole'])
            fetchedUser = db.get_user(signupUser['email'])
            registeredUserID = fetchedUser[-1][-1]
            loggedInUser = User(signupUser['firstName'], signupUser['lastName'], signupUser['email'], signupUser['phone'], registeredUserID, orgId, signupUser['clubRole'])
            session['user'] = loggedInUser.dictionary()
            session['email'] = signupUser['email']
            session['logged_in'] = True
            return redirect(url_for('user_page.user'))
        except Exception as e:
            return render_template('signup.html', form=form, roleForm=roleForm, errors=["Failed to register user - {}".format(str(e))])

    return render_template('signup.html', form=form, roleForm=roleForm, errors=[])


login_page = Blueprint('login_page', __name__, template_folder='templates')
@login_page.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in') != True:
        form = LoginForm()
        if form.validate_on_submit():
            #session['email'] = form.email.data
            email = form.email.data
            if 'utoronto' in email:
                session['valid_email'] = True
            else:
                session['valid_email'] = False
                return redirect(url_for('login_page.login'))
            
            fetchedUser = db.get_user(email)
            if ( fetchedUser == []):
                return redirect(url_for('login_page.login')) #user does not exist
            else:
                fetchedUser = fetchedUser[0]
          
            savedPassword = fetchedUser[4] #password is the 5th column in the table
            if (savedPassword != form.password.data):
                return redirect(url_for('login_page.login'))
            
            #valid login
            session['user'] = User(fetchedUser[0], fetchedUser[1], fetchedUser[2], fetchedUser[3], fetchedUser[7], fetchedUser[5], fetchedUser[6]).dictionary()
            session['email'] = fetchedUser[2]
            session['logged_in'] = True
            return redirect(url_for('user_page.user'))
          
        return render_template('login.html', logged_in=session.get('logged_in'), form=form, email=session.get('email'), validEmail=session.get('valid_email'), current_time=datetime.utcnow())
    else:
        form = LogoutForm()
        if form.validate_on_submit():
            session['user'] = None
            session['logged_in'] = False
            session['email'] = None
            session['password'] = None
            session['valid_email'] = None
            return redirect(url_for('login_page.login'))
        return render_template('login.html', logged_in=session.get('logged_in'), form=form, email=session.get('email'), current_time=datetime.utcnow())

user_page = Blueprint('user_page', __name__, template_folder='templates')
@user_page.route('/user')
def user():
    return render_template('user.html', logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())
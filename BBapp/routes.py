from flask import Flask, render_template, session, redirect, url_for, flash, Blueprint, request, jsonify
from datetime import datetime
import time
from BBapp.forms import *
from BBapp.database import Database
from BBapp.user import User
from BBapp.event import Event


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
            result = db.get_organization(signupUser['clubName'])
            if len(result) == 0:
                db.insert_organization(signupUser['clubName'],"Placeholder Email","Placeholder Description","Placeholder org type", "Placeholder Password")
                orgId = db.get_organization(signupUser['clubName'])[0][-1]
            else:
                orgId = result[0][-1]
            #orgId = 1 #default value for now

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
            return redirect(url_for('events_page.events'))
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
            return redirect(url_for('events_page.events'))

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

events_page = Blueprint('events_page', __name__, template_folder='templates')
@events_page.route('/events')
def events():
    my_events_list = []
    upcoming_events_list = []
    if session.get('logged_in') == True:
        fetchedUserCreatedEvents = db.get_user_created_events(session['user'].get("userID"), datetime.utcnow())
        #add events user has registered for (when we have registration functionality)
        if fetchedUserCreatedEvents != []:
            for event_iter in fetchedUserCreatedEvents:
                event = Event(event_iter[0], event_iter[1], event_iter[2], event_iter[3], event_iter[4], event_iter[5], event_iter[6], event_iter[7], event_iter[8], event_iter[9], event_iter[10], event_iter[11], event_iter[12])
                if (event.get_id() != -1): #check if the event was properly fetched
                    my_events_list.append(event.to_dict())
        else:
            my_events_list = False
        fetchedUpcomingEvents = db.get_all_upcoming_events(datetime.utcnow())
        if fetchedUpcomingEvents != []:
            for event_iter in fetchedUpcomingEvents:
                event = Event(event_iter[0], event_iter[1], event_iter[2], event_iter[3], event_iter[4], event_iter[5], event_iter[6], event_iter[7], event_iter[8], event_iter[9], event_iter[10], event_iter[11], event_iter[12])
                upcoming_events_list.append(event.to_dict())
        else:
            upcoming_events_list = False
    return render_template('events.html', MyEvents = my_events_list, UpcomingEvents = upcoming_events_list, logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())

user_page = Blueprint('user_page', __name__, template_folder='templates')
@user_page.route('/user')
def user():
    if session.get('logged_in') == True:
        firstName = session['user'].get("firstname")
        lastName = session['user'].get("lastname")
        phone = session['user'].get("phone")
    else:
        firstName = None
        lastName = None
        phone = None
    return render_template('user.html', first_name=firstName, last_name=lastName, phone=phone, logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())

calendar_page = Blueprint('calendar_page', __name__, template_folder='templates')
@calendar_page.route('/calendar', methods=['GET', 'POST'])
def calendar():
    return render_template('calendar.html', logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())
@calendar_page.route("/receiver", methods=['GET', 'POST'])
def receiver():
    print(session.get("email"))
    all_events = db.get_user_events(session.get("email"))

    data = []
    print(all_events)
    for event in all_events:
        event_datetime = datetime.strptime(event[3], '%Y-%m-%d %H:%M:%S')
        event_datetime_ms = time.mktime(event_datetime.timetuple()) * 1000
        data.append({"eventName" : event[0], "Location" : event[2], "date": event_datetime_ms, "color": "green"})
        print(data)

    data = jsonify(data)
    return data


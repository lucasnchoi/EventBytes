
import os
import secrets
from flask import Flask, render_template, session, redirect, url_for, flash, Blueprint, request, jsonify
from datetime import datetime
import time
from BBapp.forms import *
from BBapp.database import Database
from BBapp.user import User
from BBapp.event import Event
from BBapp import app
from PIL import Image

UPLOAD_FOLDER = './BBapp/static/profile_pics'

db = Database()

home_page = Blueprint('home_page', __name__, template_folder='templates')
@home_page.route('/')
def home():
    #return render_template('index.html', current_time=datetime.utcnow(), filtered_events=filtered_events, search_query=search_query)
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
        session['picture'] = None

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
            session['password'] = fetchedUser[4]
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

<<<<<<< HEAD

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





events_page = Blueprint('events_page', __name__, template_folder='templates')
search_page = Blueprint('filtered_event_page', __name__, template_folder='templates')
filter_dates = Blueprint('filter_date', __name__, template_folder='templates')



def search(search_query, up):
    search_results_upcoming = []
    #search_results_subscribed = []
    search_results_userCreated = []

    #searched_events_subscribed = db.search_events(search_query, True)

    if(up):
        searched_events_upcoming = db.search_events(search_query, False, datetime.utcnow())
        if searched_events_upcoming != []:
            for event_fields in searched_events_upcoming:
                event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                search_results_upcoming.append(event.to_dict())
        else:
            search_results_upcoming = False

        return search_results_upcoming

    else:
        userId = session['user'].get("userID")
        searched_events_userCreated = db.search_UserEvents(search_query, userId)
        if searched_events_userCreated != []:
            for event_fields in searched_events_userCreated:
                event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                search_results_userCreated.append(event.to_dict())
        
=======
events_page = Blueprint('events_page', __name__, template_folder='templates')
@events_page.route('/events')
def events():

    my_events_list = []
    upcoming_events_list = []
    if session.get('logged_in') == True:
        fetchedUserCreatedEvents = db.get_user_created_events(session['user'].get("userID"), datetime.utcnow())
        if fetchedUserCreatedEvents != []:
            for event_iter in fetchedUserCreatedEvents:
                event = Event(event_iter[0], event_iter[1], event_iter[2], event_iter[3], event_iter[4], event_iter[5], event_iter[6], event_iter[7], event_iter[8], event_iter[9], event_iter[10], event_iter[11], event_iter[12])
                if (event.get_id() != -1): #check if the event was properly fetched
                    my_events_list.append(event.to_dict())

        fetchedUserSubscribedEvents = db.get_user_subscribed_events(session['user'].get("userID"))
        registered_eventIDs = []
        if fetchedUserSubscribedEvents != []:
            for event_sub in fetchedUserSubscribedEvents:
                if event_sub[1] not in registered_eventIDs:
                    event_reg = db.get_event_by_id(event_sub[1])
                    for event_iter in event_reg:
                        registered_event = Event(event_iter[0], event_iter[1], event_iter[2], event_iter[3], event_iter[4], event_iter[5], event_iter[6], event_iter[7], event_iter[8], event_iter[9], event_iter[10], event_iter[11], event_iter[12])
                        my_events_list.append(registered_event.to_dict())
                        registered_eventIDs.append(event_sub[1])
        
        if fetchedUserCreatedEvents == [] and fetchedUserSubscribedEvents == []:
            my_events_list = False
        fetchedUpcomingEvents = db.get_all_upcoming_events(datetime.utcnow())
        if fetchedUpcomingEvents != []:
            for event_iter in fetchedUpcomingEvents:
                event = Event(event_iter[0], event_iter[1], event_iter[2], event_iter[3], event_iter[4], event_iter[5], event_iter[6], event_iter[7], event_iter[8], event_iter[9], event_iter[10], event_iter[11], event_iter[12])
                upcoming_events_list.append(event.to_dict())
>>>>>>> cda10fc3934c10659c04f2a094dfdea22531d98b
        else:
            search_results_userCreated = False
        
        return search_results_userCreated



@events_page.route('/events', methods= ['GET', 'POST'])
def events():
    if (request.method == 'GET'):
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


    else: #POST
    
        search_query = request.form.get('search_value')
        searched_upcoming_events = []
        searched_my_events = []
        print(search_query)
        searched_upcoming_events = search(search_query, True)
        print(searched_upcoming_events, flush=True)
        searched_my_events = search(search_query, False)
        print(searched_my_events, flush=True)
        for event in searched_upcoming_events:
            print(event)

        return render_template('events.html', MyEvents = searched_my_events, UpcomingEvents = searched_upcoming_events, logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())
       # elif (type == 'filter'):
         #   print("filtering")




@search_page.route('/filter', methods= [ 'POST'])
def filter():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    if start_date is not None:

        if end_date is None:
            end_date = start_date
            events_byDate = db.filter_events_byDate(start_date, end_date, False, datetime.utcnow())
            if events_byDate != []:
                for event_fields in events_byDate:
                    event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                    date_filtered_upcomingEvents.append(event.to_dict())
            else:
                date_filtered_upcomingEvents = False

        userId = session['user'].get("userID")
        myEvents_byDate = db.filter_UserEvents_byDate(start_date, end_date, userId)
        if myEvents_byDate != []:
            for event_fields in myEvents_byDate:
                event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                date_filtered_myEvents.append(event.to_dict())
        else:
            date_filtered_myEvents = False


    return render_template('events.html', MyEvents = date_filtered_myEvents, UpcomingEvents = date_filtered_upcomingEvents, logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())


    

def filter_type():

    type_filtered_upcomingEvents = [];
    type_filtered_myEvents = []
    filter_type = request.args.get('filter_query')

    filtered_events_upcoming = db.filter_event_by_type(filter_type, False, datetime.utcnow())
    userId = session['user'].get("userID")
    filtered_events_userCreated = db.filter_UserEvent_by_type(filter_type, userId)

    if filtered_events_upcoming != []:
            for event_fields in filtered_events_upcoming:
                event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                type_filtered_upcomingEvents.append(event.to_dict())
    else:
        type_filtered_upcomingEvents = False
    
    if filtered_events_userCreated != []:
            for event_fields in filtered_events_userCreated:
                event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                type_filtered_myEvents.append(event.to_dict())
        
    else:
        type_filtered_myEvents = False;

    return render_template('events.html', UpcomingEvents = type_filtered_upcomingEvents, MyEvents = type_filtered_myEvents, current_time=datetime.utcnow())



registration_page = Blueprint('registration_page', __name__, template_folder='templates')
@registration_page.route('/events/registration', methods=['POST'])
def registration():
    eventID = request.get_json().get("eventID")
    if request.method == 'POST' and eventID != None and session.get('logged_in') == True:
        db.insert_event_subscriber(session['user'].get("userID"), eventID)
        return redirect(url_for('events_page.events'))
    else:
        print("Error: eventID is None or user is not logged in")
        return redirect(url_for('events_page.events'))
        
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path + 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


user_page = Blueprint('user_page', __name__, template_folder='templates')
@user_page.route('/user', methods = ['GET', 'POST'])
def user():
    form = UpdateAccountForm()
    if session.get('logged_in') == True:
        
        if request.method == "POST":
            updateUser = {}
            updateUser["firstname"] = form.firstname.data
            updateUser["lastname"] = form.lastname.data
            updateUser["email"] = form.email.data
            updateUser["password"] = form.password.data
            updateUser["phone"] = form.phone.data
            db.delete_user(updateUser['email'])
            db.insert_user(updateUser['firstname'],updateUser['lastname'],updateUser['email'],updateUser['phone'],updateUser['password'],session['user'].get('OrgId'), session['user'].get('OrgRole'))
            session['user'] = User(updateUser['firstname'], updateUser['lastname'], updateUser['email'], updateUser['phone'], session['user'].get("userID"), session['user'].get('orgID'), session['user'].get('orgRole')).dictionary()
            session['password'] = updateUser["password"]
            session['email'] = updateUser["email"]
            if form.picture.data:
                file1 = form.picture.data.read()
                path = os.path.join(UPLOAD_FOLDER, form.picture.data.filename)
                with open(path, 'wb') as file2:
                    file2.write(file1)

                session['picture'] = form.picture.data.filename
                print(session['picture'])
            flash('updated successfully', 'success')
            return redirect(url_for('user_page.user'))
        elif request.method == "GET":

            form.firstname.data = session['user'].get("firstname")
            form.lastname.data  = session['user'].get("lastname")
            form.phone.data  = session['user'].get("phone")
            form.email.data =session.get('email')
            form.password.data = session.get('password')
        image_file = url_for('static', filename='profile_pics/' + session['picture']) if session and 'picture' in session and session['picture'] is not None else url_for('static', filename='profile_pics/default.jpg')
        form.picture.data = image_file


        return render_template('user.html', phone = session['user'].get("phone"), email =  session.get('email'), first_name = session['user'].get("firstname"), last_name = session['user'].get("lastname") ,form = form, image_file = image_file, logged_in=session.get('logged_in'), current_time=datetime.utcnow())
    else:


        firstName = None
        lastName = None
        phone = None
        return redirect(url_for('login_page.login'))

calendar_page = Blueprint('calendar_page', __name__, template_folder='templates')
@calendar_page.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if session.get('logged_in') == True:
        return render_template('calendar.html', logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())
    else:
        firstName = None
        lastName = None
        phone = None
        return render_template('user.html', first_name=firstName, last_name=lastName, phone=phone, logged_in=session.get('logged_in'), email=session.get('email'), current_time=datetime.utcnow())

@calendar_page.route("/receiver", methods=['GET', 'POST'])
def receiver():
    #Include user's registered events as well as user's created events
    all_events = db.get_user_events(session.get("email"))
    userID = (db.get_user(session.get("email")))[-1][-1]
    all_user_events = db.get_user_created_events(userID, datetime.utcnow())
    for events in all_user_events:
        if events not in all_events:
            all_events.append(events)
    data = []
    for event in all_events:
        event_datetime = datetime.strptime(event[3], '%Y-%m-%d %H:%M:%S')
        event_datetime_ms = time.mktime(event_datetime.timetuple()) * 1000
        data.append({"eventName" : event[0], "Location" : event[2], "date": event_datetime_ms, "color": "green"})

    data = jsonify(data)
    return data

force_reload_page = Blueprint('forceReload', __name__, template_folder='templates')
@force_reload_page.route('/forceReload', methods=['GET'])
def forceReload():
    try:
        db.force_reconnect()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))
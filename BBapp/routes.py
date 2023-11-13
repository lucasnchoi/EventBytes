from flask import Flask, render_template, session, redirect, url_for, flash, Blueprint, request
from datetime import datetime
from BBapp.forms import *
from BBapp.database import Database
from BBapp.user import User
from BBapp.event import Event


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


def search():
    search_results_upcoming = []
    #search_results_subscribed = []
    search_results_userCreated = []

    if session.get('logged_in') == True and request.method == 'GET':

        search_query = request.args.get('user_query')
        searched_events_upcoming = db.search_events(search_query, False, datetime.utcnow())
        #searched_events_subscribed = db.search_events(search_query, True)
        userId = session['user'].get("userID")
        searched_events_userCreated = db.search_UserEvents(search_query, userId)

        if searched_events_upcoming != []:
            for event_fields in searched_events_upcoming:
                event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                search_results_upcoming.append(event.to_dict())
        else:
            search_results_upcoming = False
    
        if searched_events_userCreated != []:
            for event_fields in searched_events_userCreated:
                event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                search_results_userCreated.append(event.to_dict())
        
        else:
            search_results_userCreated = False;

    return render_template('events.html', UpcomingEvents = search_results_upcoming, MyEvents = search_results_userCreated, current_time=datetime.utcnow())



def filter_date():

    date_filtered_upcomingEvents = [];
    date_filtered_myEvents = []
    start_date = request.args.get('start-date')
    end_date = request.args.get('end-date')

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


    return render_template('events.html', UpcomingEvents = date_filtered_upcomingEvents, MyEvents = date_filtered_myEvents, current_time=datetime.utcnow())


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



user_page = Blueprint('user_page', __name__, template_folder='templates')
@user_page.route('/user', methods = ['GET', 'POST'])
def user():
    form = UpdateAccountForm()
    if session.get('logged_in') == True:
        image_file = url_for('static', filename = 'uoft-logo')
        if form.validate_on_submit():
            updateUser = {}
            updateUser["firstname"] = form.firstname.data
            updateUser["lastname"] = form.lastname.data
            updateUser["email"] = form.email.data
            updateUser["password"] = form.password.data
            updateUser["phone"] = form.phone.data
            print(updateUser)
            db.delete_user(updateUser['email'])
            db.insert_user(updateUser['firstname'],updateUser['lastname'],updateUser['email'],updateUser['phone'],updateUser['password'],session['user'].get('OrgId'), session['user'].get('OrgRole'))
            session['user'] = User(updateUser['firstname'], updateUser['lastname'], updateUser['email'], updateUser['phone'], session['user'].get("userID"), session['user'].get('orgID'), session['user'].get('orgRole')).dictionary()
            session['password'] = updateUser["password"]
            session['email'] = updateUser["email"]
            flash('updated successfully', 'success')
            print(session['user'])
            print(updateUser)
            return redirect(url_for('user_page.user'))
        elif request.method == "GET":
            
            form.firstname.data = session['user'].get("firstname")
            form.lastname.data  = session['user'].get("lastname")
            form.phone.data  = session['user'].get("phone")
            form.email.data =session.get('email')
            form.password.data = session.get('password')
            
        return render_template('user.html', phone = session['user'].get("phone"), email =  session.get('email'), first_name = session['user'].get("firstname"), last_name = session['user'].get("lastname") ,form = form, image_file = image_file, logged_in=session.get('logged_in'), current_time=datetime.utcnow())
    else:


        firstName = None
        lastName = None
        phone = None
        return redirect(url_for('login_page.login'))


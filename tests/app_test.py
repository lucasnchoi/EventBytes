import pytest
import datetime
from BBapp import app
from BBapp.database import Database

db = Database()

@pytest.fixture
def client(): #Peter
    app.debug = True
    client = app.test_client()
    yield client

def signup(client, email, firstName,lastName, phone, password, confirmPassword, clubRepresentative, clubName, clubRole): #Peter
    return client.post('/signup', data=dict(
        email=email,
        firstName=firstName,
        lastName=lastName,
        phone=phone,
        password=password,  
        confirmPassword=confirmPassword,
        clubRepresentative=clubRepresentative,
        clubName=clubName,
        clubRole=clubRole
    ), follow_redirects=False)

def test_signup(client): #Peter
    """Test signup route"""
    rv = signup(client, 'test@mail.utoronto.ca', 'test','lastName','1234567890', 'password', 'noMatchingPassword', 'No', '', '') #no matching passwords
    assert rv.status_code == 200 and "Passwords do not match" in str(rv.data)
    rv = signup(client, 'test@gmail.com', 'test','lastName','1234567890', 'password', 'password', 'No', '', '') #non uoft email
    assert rv.status_code == 200 and "Please use a valid UofT email address" in str(rv.data)
    rv = signup(client, 'test@mail.utoronto.ca', 'test', 'lastName','1234567890', 'password', 'password', 'Yes', '', '') #empty club name
    assert rv.status_code == 200 and "Please enter a club name" in str(rv.data)
    rv = signup(client, 'valid1Test@mail.utoronto.ca', 'test', 'lastName','1234567890', 'password', 'password', 'No', '', '') #valid signup of non club representative
    assert rv.status_code == 302 and rv.location == '/events'
    db.delete_user('valid1Test@mail.utoronto.ca') 
    rv = signup(client, 'valid2Test@mail.utoronto.ca', 'test', 'lastName','1234567890', 'password', 'password', 'Yes', 'Developer Club', 'President') #valid signup of club representative
    assert rv.status_code == 302 and rv.location == '/events'
    db.delete_user('valid2Test@mail.utoronto.ca') 


def login(client, email, password): #Nuova
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

def test_login(client): #Nuova
    # Test if login page renders correctly
    response = client.get('/login')
    assert response.status_code == 200, "Login page did not render correctly"

    # Test for invalid email login
    response = login(client, 'invalid@notutoronto.com', 'password')
    assert response.status_code == 200, "Invalid email login did not redirect to login page"

    # Test for incorrect password login
    response = login(client, 'valid@utoronto.ca', 'wrongpassword')
    assert response.status_code == 200, "Incorrect password login did not redirect to login page"

    # Test for successful login
    response = login(client, 'valid@utoronto.ca', 'password')
    assert b'user' in response.data, "Successful login did not redirect to user page or did not show expected content"


def test_event(client):
    """Test event page"""
    rv = client.get('/events')
    assert rv.status_code == 200 and '<h1>Please <a href="/login">log in</a> first. </h1>' in str(rv.data), "Event page accessible without logging in"
    rv = signup(client, 'eventTest@mail.utoronto.ca', 'test', 'lastName','1234567890', 'password', 'password', 'No', '', '')
    rv = client.get('/events')
    assert rv.status_code == 200 and "Events Dashboard" in str(rv.data), "Event page unaccessible after logging in"
    db.delete_user('eventTest@mail.utoronto.ca') 

def test_event_dashboard_my_events(client):
    """Test event page my events"""
    db.delete_user('myEventsTest@mail.utoronto.ca')
    rv = signup(client, 'myEventsTest@mail.utoronto.ca', 'test', 'lastName','1234567890', 'password', 'password', 'No', '', '')
    rv = client.get('/events')
    assert rv.status_code == 200 and "My Events:" and "Upcoming Events:" in str(rv.data), "Event page unaccessible after logging in"
    rv = createEvent(client, 'MyEventTestEvent', 'Other', datetime.datetime(2025, 11, 7, 15, 10), 10, 'testLocation', 'testDetails', 'testBooking', 'testAccommodation', 'testRequisite', 'testContact', 'No')
    assert rv.status_code == 200  and "Event created successfully" in str(rv.data), "Event creation failed"
    rv = client.get('/events')
    assert rv.status_code == 200 and "MyEventTestEvent" and "testLocation" in str(rv.data), "User's created events not displayed"
    db.delete_event('MyEventTestEvent', 0, 'testLocation', datetime.datetime(2025, 11, 7, 15, 10))
    db.delete_user('myEventsTest@mail.utoronto.ca')

def test_user(client):
    """Test user page"""
    db.delete_user('userTest@mail.utoronto.ca') 
    rv = client.get('/user')
    print(str(rv.data))
    assert rv.status_code == 200 and '<h1>Please <a href="/login">log in</a> first.</h1>' in str(rv.data), "User page accessible without logging in"
    rv = signup(client, 'userTest@mail.utoronto.ca', 'test', 'lastName','1234567890', 'password', 'password', 'No', '', '')
    rv = client.get('/user')
    assert rv.status_code == 200, "User page unaccessible after logging in"
    print(str(rv.data))
    assert "test lastName" and "User Profile" in str(rv.data), "Incorrect user profile names"
    assert "email:" in str(rv.data), "Incorrect user profile email"
    assert "phone: 1234567890" in str(rv.data), "Incorrect user profile phone"
    db.delete_user('userTest@mail.utoronto.ca') 

def createEvent(client, name, type, time, size, location, details, booking, accommodation, requisite, contact, organizationHosted): 
    return client.post('/create_event', data=dict(
        name=name,
        type=type,
        time=time,
        size=size,
        location=location,
        details=details,
        booking=booking,
        accommodation=accommodation,
        requisite=requisite,
        contact=contact,
        organizationHosted=organizationHosted
    ), follow_redirects=False)


def test_createEvent(client):
    """Test create_event route"""
    db.delete_user('eventCreator@mail.utoronto.ca')
    rv = signup(client, 'eventCreator@mail.utoronto.ca', 'test', 'lastName','1234567890', 'password', 'password', 'Yes', 'Developer Club', 'President')
    rv = createEvent(client, 'testEvent', 'Other', datetime.datetime(2025, 11, 7, 15, 10), 10, 'testLocation', 'testDetails', 'testBooking', 'testAccommodation', 'testRequisite', 'testContact', 'No') #valid event creation for personal
    assert rv.status_code == 200  and "Event created successfully" in str(rv.data), "Event creation failed"
    db.delete_event('testEvent', 0, 'testLocation', datetime.datetime(2025, 11, 7, 15, 10)) #delete event after test
    rv = createEvent(client, 'testEvent', 'Other', datetime.datetime(2025, 11, 7, 15, 10), 10, 'testLocation', 'testDetails', 'testBooking', 'testAccommodation', 'testRequisite', 'testContact', 'Yes') #valid event creation for org
    assert rv.status_code == 200  and "Event created successfully" in str(rv.data), "Event creation failed"
    db.delete_event('testEvent', 1, 'testLocation', datetime.datetime(2025, 11, 7, 15, 10)) #delete event after test
    rv = createEvent(client, 'testEvent', 'Other', datetime.datetime(2021, 11, 7, 15, 10), 10, 'testLocation', 'testDetails', 'testBooking', 'testAccommodation', 'testRequisite', 'testContact', 'No') #invalid event creation time
    assert "Events cannot be created in the past" in str(rv.data)
    rv = createEvent(client, 'testEvent', 'Other', datetime.datetime(2025, 11, 7, 15, 10), -1, 'testLocation', 'testDetails', 'testBooking', 'testAccommodation', 'testRequisite', 'testContact', 'No') #invalid event creation size
    assert "Attendee size cannot be negative" in str(rv.data)
    db.delete_user('eventCreator@mail.utoronto.ca') #delete user after test

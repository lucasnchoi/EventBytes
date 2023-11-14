import pytest
import datetime
from BBapp import app
from BBapp.database import Database

@pytest.fixture
def client():
    app.debug = True
    client = app.test_client()
    yield client

db = Database()

def signup(client, email, firstName,lastName, phone, password, confirmPassword, clubRepresentative, clubName, clubRole):
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
def test_calendarLoad(client):
    #Test loading of Calendar Events
    db.delete_user('CalendarTest@mail.utoronto.ca')
    test = client.get('/calendar')
    assert test.status_code == 200 and 'Please <a href="/login">log in</a> first.' in str(test.data), "Calendar did not redirect to user login when not logged in"

    test = signup(client, 'CalendarTest@mail.utoronto.ca', 'test', 'lastName', '1234567890', 'password', 'password',
                    'No', '', '')
    assert test.status_code == 302 and test.location == '/events', "Error with signup page redirect"
    test = client.get('/calendar')
    assert test.status_code == 200, "Error loading calendar"


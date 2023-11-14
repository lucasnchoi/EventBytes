import unittest
from flask import Flask
from datetime import datetime
from flask.testing import FlaskClient
from database import Database
from event import Event

class TestEventHubFeatures(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

        # Use a test database
        self.db = Database(host="sql5.freesqldatabase.com", user="sql5659789", password="ELhaR4pm34", database="sql5659789")
        
        # Initialize your database with test data or mock data
        self.initialize_test_data()

    def initialize_test_data(self):
        self.insert_organization("ABC Corp", "exploreABC@gmail.com", "we help with LIFE exploration", "networking", "1234", 2, "organizor", 2)
        self.insert_organization("DEF Corp", "exploreDEF@gmail.com", "we help", "networking", "1224", 1, "organizor", 6)
        self.insert_organization("TEP Corp", "exploreTEP@gmail.com", "we also help", "guidance", "1534", 1, "organizor", 8)
        self.insert_event_org_parent("please come", "ABC Corp")
        self.db.insert_event('my event 1', 'Other','location a', "2023-12-03T08:30", 'details 1', 'booking 1', 'accommodation 1', 'requisite 1',10, 'contact 1',1, 1, 1)
        self.db.insert_event("career fair", "networking", "ex200", "2023-14-03T09:30", "please come", "none", "none", "none", 100, "johnsmith@gmail.com", 2, 2, 2)
        self.db.insert_event("my event 2", "Other", "location a", "2023-10-03T08:30", "please come", "none", "none", "none", 100, "johnCollins@gmail.com", 3, 3, 3)
        self.db.insert_event("cultural fair", "networking", "ex200", "2023-14-03T09:30", "please come", "none", "none", "none", 100, "johnhenson@gmail.com", 2, 2, 4)



    def form_event_list(self, name, uid, time=None):
       if time is None:
        org_search_result = []
        searched_events_userCreated = self.db.search_UserEvents(name, uid)
        for event_fields in searched_events_userCreated:
                    event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                    org_search_result.append(event.to_dict())
        
       else:
        org_search_result = []
        searched_events_userCreated = self.db.search_events(name, False, time)
        for event_fields in searched_events_userCreated:
                    event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                    org_search_result.append(event.to_dict())
        
       return org_search_result
    

    def retrieve_event_list(self, name, location, time):
        
        org_search_result = []
        searched_events_userCreated = self.db.get_event(name, location, time)
        for event_fields in searched_events_userCreated:
                    event = Event(event_fields[0], event_fields[1], event_fields[2], event_fields[3], event_fields[4], event_fields[5], event_fields[6], event_fields[7], event_fields[8], event_fields[9], event_fields[10], event_fields[11], event_fields[12])
                    org_search_result.append(event.to_dict())



    def test_search_events(self):
       # response = self.client.get()
       self.assertEqual(self.db.search_events("career fair", False, datetime.utcnow()), self.db.get_event("career fair", "ex200", "2023-14-03T09:30"))
       
"""

       org_search_result = self.form_event_list("ABC Corp", 2)
       org_correct_result = self.retrieve_event_list("ABC Corp", "ex200", "2023-14-03T09:30")
      
       self.assertEqual(org_search_result, org_correct_result)
 
    

    def test_events_for_selected_date(self):
        response = self.client.get('/events_for_selected_date?date=2023-11-09')
        self.assertEqual(response.status_code, 200)


    def test_sort_events(self):
        response = self.client.get('/sort_events')
        self.assertEqual(response.status_code, 200)
    

if __name__ == '__main__':
    unittest.main()

    """
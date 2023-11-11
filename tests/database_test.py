import unittest
from datetime import datetime
from BBapp.database import Database  

class TestEventClass(unittest.TestCase):

    def setUp(self):
        # Create an instance of event for testing
        self.database = Database()

    def test_connection(self):
        command = "SHOW DATABASES"
        self.database.mycursor.execute(command)
        self.assertEqual(list(self.database.mycursor)[1][0],'sql5659789')

    def test_basic_functions_users(self):
        #insertion:
        results = self.database.insert_user("Peter","Jonathan","a@mail.utoronto.ca","64712345","password1234",1,"President")
        self.database.mycursor.execute('SELECT last_insert_id() from users')
        user_id = list(self.database.mycursor)[0][0]

        #get:
        results = self.database.get_user("a@mail.utoronto.ca")
        self.assertEqual(results[-1],('Peter','Jonathan','a@mail.utoronto.ca','64712345','password1234',1,'President',user_id))

        """
        command = "ALTER TABLE users AUTO_INCREMENT = %s" #reset id counter
        self.database.mycursor.execute(command,(batch_id,))
        """

        #delete:
        results = self.database.delete_user("a@mail.utoronto.ca")

        #get:
        results = self.database.get_user("a@mail.utoronto.ca")
        self.assertEqual(results,[])

    def test_basic_functions_events(self):
        #insertion:
        timeNow = str(datetime.now())
        results = self.database.insert_event('my event 1', 'Other','location a', str(timeNow), 'details 1', 'booking 1', 'accommodation 1', 'requisite 1',10, 'contact 1',1,1)
        self.database.mycursor.execute('SELECT last_insert_id() from events')
        batch_id = list(self.database.mycursor)[0][0]

        #get:
        results = self.database.get_event('my event 1','location a', str(timeNow))
        self.assertEqual(results[-1],('my event 1', 'Other','location a', str(timeNow), 'details 1', 'booking 1', 'accommodation 1', 'requisite 1', 10, 'contact 1',1,1,batch_id))

        """
        command = "ALTER TABLE users AUTO_INCREMENT = %s" #reset id counter
        self.database.mycursor.execute(command,(batch_id,))
        """

        #delete:
        results = self.database.delete_event('my event 1','location a', str(timeNow))

        #get:
        results = self.database.get_event('my event 1', 'location a',str(timeNow))
        self.assertEqual(results,[])
    
    def test_basic_functions_organizations(self):
        #insertion:
        results = self.database.insert_organization("Peter", "a@mail.utoronto.ca", "my description", "my type", "1234")
        self.database.mycursor.execute('SELECT last_insert_id() from organizations')
        batch_id = list(self.database.mycursor)[0][0]

        #get:
        results = self.database.get_organization("Peter")
        self.assertEqual(results[-1],('Peter', 'a@mail.utoronto.ca', "my description", "my type", '1234', batch_id))

        """
        command = "ALTER TABLE users AUTO_INCREMENT = %s" #reset id counter
        self.database.mycursor.execute(command,(batch_id,))
        """

        #delete:
        results = self.database.delete_organization("Peter")

        #get:
        results = self.database.get_organization("Peter")
        self.assertEqual(results,[])

    
    
    def test_basic_functions_event_subscriber(self):
        #setup:
        results = self.database.insert_user("Peter","Jonathan","a@mail.utoronto.ca","64712345","password1234",1,"President")
        timeNow = str(datetime.now())
        results = self.database.insert_event('my event 1', 'Other','location a', str(timeNow), 'details 1', 'booking 1', 'accommodation 1', 'requisite 1',10, 'contact 1',1,1)

        #insertion:
        results = self.database.insert_event_subscriber("a@mail.utoronto.ca", "my event 1", "location a",str(timeNow))
        self.database.mycursor.execute('SELECT last_insert_id() from event_subs')
        ESID = list(self.database.mycursor)[0][0]

        #get:
        userID = self.database.get_user("a@mail.utoronto.ca")[-1][-1]
        eventID = self.database.get_event("my event 1", "location a", str(timeNow))[-1][-1]

        results = self.database.get_event_subscriber("a@mail.utoronto.ca","my event 1", "location a", str(timeNow))
        self.assertEqual(results[-1],(userID,eventID,ESID))

        results = self.database.get_user_events("a@mail.utoronto.ca")
        self.assertEqual(results[0][:4],('my event 1', 'Other','location a', str(timeNow)))

        results = self.database.get_event_subscribers("my event 1", "location a", str(timeNow))
        self.assertEqual(results[0][:4],('Peter', 'Jonathan', 'a@mail.utoronto.ca', '64712345'))

        """
        command = "ALTER TABLE users AUTO_INCREMENT = %s" #reset id counter
        self.database.mycursor.execute(command,(batch_id,))
        """

        #delete:
        results = self.database.delete_event_subscriber(userID,eventID)
        results = self.database.delete_user("a@mail.utoronto.ca")
        results = self.database.delete_event('my event 1','location a', str(timeNow))
        

    def test_basic_functions_org_subscriber(self):
        #setup:
        results = self.database.insert_user("Peter","Jonathan","a@mail.utoronto.ca","64712345","password1234",1,"President")
        results = self.database.insert_organization("Peter", "a@mail.utoronto.ca", "my description", "my type", "1234")

        #insertion:
        results = self.database.insert_org_subscriber("a@mail.utoronto.ca", "Peter")
        self.database.mycursor.execute('SELECT last_insert_id() from org_subs')
        OSID = list(self.database.mycursor)[0][0]

        #get:
        userID = self.database.get_user("a@mail.utoronto.ca")[-1][-1]
        orgID = self.database.get_organization("Peter")[-1][-1]

        results = self.database.get_org_subscriber("a@mail.utoronto.ca","Peter")
        self.assertEqual(results[-1],(userID,orgID,OSID))

        results = self.database.get_user_orgs("a@mail.utoronto.ca")
        self.assertEqual(results[0][:4],('Peter', 'a@mail.utoronto.ca', 'my description', 'my type'))

        results = self.database.get_org_subscribers("Peter")
        self.assertEqual(results[0][:4],('Peter', 'Jonathan', 'a@mail.utoronto.ca', '64712345'))

        """
        command = "ALTER TABLE users AUTO_INCREMENT = %s" #reset id counter
        self.database.mycursor.execute(command,(batch_id,))
        """

        #delete:
        results = self.database.delete_org_subscriber(userID,orgID)
        results = self.database.delete_user("a@mail.utoronto.ca")
        results = self.database.delete_organization("Peter")

    def test_basic_functions_org_members(self):
        #setup:
        results = self.database.insert_user("Peter","Jonathan","a@mail.utoronto.ca","64712345","password1234",1,"President")
        results = self.database.insert_organization("Peter", "a@mail.utoronto.ca", "my description", "my type", "1234")

        #insertion:
        results = self.database.insert_org_member("a@mail.utoronto.ca", "president", "Peter")
        self.database.mycursor.execute('SELECT last_insert_id() from org_mems')
        OMID = list(self.database.mycursor)[0][0]

        #get:
        userID = self.database.get_user("a@mail.utoronto.ca")[-1][-1]
        orgID = self.database.get_organization("Peter")[-1][-1]

        results = self.database.get_org_member("a@mail.utoronto.ca","Peter")
        self.assertEqual(results[-1],(userID,"president",orgID,OMID))

        """
        command = "ALTER TABLE users AUTO_INCREMENT = %s" #reset id counter
        self.database.mycursor.execute(command,(batch_id,))
        """

        #delete:
        results = self.database.delete_org_member(userID,orgID)
        results = self.database.delete_user("a@mail.utoronto.ca")
        results = self.database.delete_organization("Peter")

    def test_basic_functions_event_org_parents(self):
        #setup:
        timeNow = str(datetime.now())
        results = self.database.insert_event('my event 1', 'Other','location a', str(timeNow), 'details 1', 'booking 1', 'accommodation 1', 'requisite 1',10, 'contact 1',1,1)
        results = self.database.insert_organization("Peter", "a@mail.utoronto.ca", "my description", "my type", "1234")

        #insertion:
        results = self.database.insert_event_org_parent("my event 1", "location a",str(timeNow), "Peter")
        self.database.mycursor.execute('SELECT last_insert_id() from event_parent_org')
        EPOID = list(self.database.mycursor)[0][0]

        #get:
        eventID = self.database.get_event("my event 1", "location a", str(timeNow))[-1][-1]
        orgID = self.database.get_organization("Peter")[-1][-1]

        results = self.database.get_event_org_parent("my event 1", "location a",str(timeNow), "Peter")
        self.assertEqual(results[-1],(eventID,orgID,EPOID))

        """
        command = "ALTER TABLE users AUTO_INCREMENT = %s" #reset id counter
        self.database.mycursor.execute(command,(batch_id,))
        """

        #delete:
        results = self.database.delete_org_member(eventID,orgID)
        results = self.database.delete_event('my event 1','location a', str(timeNow))
        results = self.database.delete_organization("Peter")


if __name__ == '__main__':
    unittest.main()
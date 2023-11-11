import unittest
from BBapp.organization import Organization 

class TestEventClass(unittest.TestCase):

    def setUp(self):
        # Create an instance of event for testing
        self.organizaion = Organization(
            name = "Test Name",
            email = "Test@mail.utoronto.ca",
            description = "Test Description",
            organization_type = "Test Type",
            password = "test password"  
        )

    def test_to_dict(self):
        event_dict = self.organizaion.to_dict()
        self.assertIsInstance(event_dict, dict)             #is a dict
        self.assertEqual(event_dict["name"], "Test Name")  #verifies the value to each pair is correct
        self.assertEqual(event_dict["email"], "Test@mail.utoronto.ca")
        self.assertEqual(event_dict["description"], "Test Description")
        self.assertEqual(event_dict["type"], "Test Type")
        self.assertEqual(event_dict["password"], "test password")
       
        
    def test_change_name(self):
        self.organizaion.change_name("New organization Name")
        self.assertEqual(self.organizaion.get_name(), "New organization Name")

if __name__ == '__main__':
    unittest.main()
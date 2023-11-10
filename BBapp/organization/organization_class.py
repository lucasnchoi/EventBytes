from datetime import datetime 

class Organization:

#MANDATORY fields: name, type, date/time, place, and description
#These must be provided by user before an event can be created. (Inform user on front end, * for mandatory fields)

    def __init__(self, name, email, description, organization_type, password = ''):
        self._name = name                   #str
        self.email = email                 #str
        self.description = description         #str
        self.type = organization_type      #str   front-end: maybe have tags for user to select when creating event? 
        self.password = password 



#Method to convert obj instance into dictionary - may be convenient when working with flask and MongoDB later

    def to_dict(self):

        event_dict = {
           "name": self._name,
           "email": self.email,
           "type": self.type,
           "description": self.description,    
           "password": self.password
        }  

        return event_dict


#Accessor and mutator methods for private members: booking, place, time, contacts, requisite, and name

    def get_email(self):
        return self.email

    def change_name(self, new_name):
        self._name = new_name

    def get_name(self):
        return self._name
    
    def change_description(self, new_desc):
        self.description = new_desc

    def get_description(self):
        return self.description
    
    def change_type(self, new_type):
        self.type = new_type

    def get_type(self):
        return self.type
    
    def print_all_attributes(self):

        if self._contact is not None:
            message = "\n"
            for pair in self._contact:
                message += f"{pair[0]}: {pair[1]}\n"

        if self._contact == []:
            message = " None"

        print("\Organizaion name: " + self.get_name() + "\Organization type: " + self.type + "\nWhat this org is about: " + self.description)

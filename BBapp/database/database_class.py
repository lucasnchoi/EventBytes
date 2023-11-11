import mysql.connector
class Database:
    def __init__(self):
        self.mydb = mysql.connector.connect(
        host="sql5.freesqldatabase.com",
        user="sql5659789",
        password="ELhaR4pm34",
        database = "sql5659789",
        port = "3306"
        )

        self.mycursor = self.mydb.cursor()
    #Class tables:

    def insert_user(self, firstName,lastName, email, phone, password, orgID, orgRole): #enforce unique uoft email
        command = "INSERT INTO users (firstName,lastName, email, phone, password, orgID, orgRole) VALUES (%s, %s, %s, %s, %s, %s, %s)" 
        self.mycursor.execute(command,(firstName,lastName, email, phone, password, orgID, orgRole))
        result = self.mycursor.fetchall() #incase later we want to see results
        self.mydb.commit() 
        return result
        
    def insert_event(self, name, type, location, time, details, booking, accommodation, requisite, size, contact, organizationId, creatorId): 
        command = "INSERT INTO events (name, type, location, time, details, booking, accommodation, requisite, size, contact, organizationId, creatorId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)"
        self.mycursor.execute(command,(name, type, location, time, details, booking, accommodation, requisite, size, contact, organizationId, creatorId))
        self.mycursor.execute('SELECT last_insert_id() from events') #get the id of the event we just inserted
        batch_id = list(self.mycursor)[0][0]
        self.mydb.commit()
        return batch_id

    def insert_organization(self, name, email, description, org_type, password): #enforce unique names
        command = "INSERT INTO organizations (name, email, description, organization_type, password) VALUES (%s, %s, %s, %s, %s)" 
        self.mycursor.execute(command,(name,email,description, org_type, password))
        result = self.mycursor.fetchall() #incase later we want to see results
        self.mydb.commit()
        return result

    def delete_user(self, email): 
        command = "DELETE FROM users WHERE email = %s" 
        self.mycursor.execute(command,(email,))
        self.mydb.commit()
        
    def delete_event(self, name, location, time): #assume events may have same names, eg recurring meetings
        command = "DELETE FROM events WHERE name = %s AND location = %s AND time = %s" 
        self.mycursor.execute(command,(name,location,time))
        self.mydb.commit()

    def delete_organization(self, name): 
        command = "DELETE FROM organizations WHERE name = %s" 
        self.mycursor.execute(command,(name,))
        self.mydb.commit()

    def get_user(self, email):
        command = "SELECT * FROM users WHERE email = %s" 
        self.mycursor.execute(command,(email,))
        result = self.mycursor.fetchall()
        return result 

    def get_event(self, name, location, time):
        command = "SELECT * FROM events WHERE name = %s AND location = %s AND time = %s" 
        self.mycursor.execute(command,(name,location,time))
        result = self.mycursor.fetchall()
        return result 
    
    def get_all_upcoming_events(self, current_time):
        command = "SELECT * FROM events WHERE time > %s ORDER BY time" 
        self.mycursor.execute(command,(current_time,))
        result = self.mycursor.fetchall()
        return result
    
    def get_user_created_events(self, userID, current_time):
        command = "SELECT * FROM events WHERE creatorId = %s AND time > %s ORDER BY time" 
        self.mycursor.execute(command,(userID, current_time))
        result = self.mycursor.fetchall()
        return result

    def get_organization(self, name):
        command = "SELECT * FROM organizations WHERE name = %s" 
        self.mycursor.execute(command,(name,))
        result = self.mycursor.fetchall()
        return result 
    
    #relationship tables:
    
    def insert_event_subscriber(self, user_email, name,location,time):
        userID = self.get_user(user_email)[-1][-1]
        eventID = self.get_event(name,location,time)[-1][-1]

        command = "INSERT INTO event_subs (userID, eventID) VALUES (%s, %s)"
        self.mycursor.execute(command,(userID,eventID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def insert_org_subscriber(self, user_email, org_name):
        userID = self.get_user(user_email)[-1][-1]
        orgID = self.get_organization(org_name)[-1][-1]

        command = "INSERT INTO org_subs (userID, orgID) VALUES (%s, %s)"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def insert_org_member(self, user_email, org_role, org_name):
        userID = self.get_user(user_email)[-1][-1]
        orgID = self.get_organization(org_name)[-1][-1]

        command = "INSERT INTO org_mems (userID, orgRole, orgID) VALUES (%s, %s, %s)"
        self.mycursor.execute(command,(userID, org_role, orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def insert_event_org_parent(self, name,location,time, org_name):
        eventID = self.get_event(name,location,time)[-1][-1]
        orgID = self.get_organization(org_name)[-1][-1]

        command = "INSERT INTO event_parent_org (eventID, orgID) VALUES (%s, %s)"
        self.mycursor.execute(command,(eventID, orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result

    def delete_event_subscriber(self, userID, eventID):
        command = "DELETE FROM event_subs WHERE userID = %s AND eventID = %s" 
        self.mycursor.execute(command,(userID, eventID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def delete_org_subscriber(self, userID, orgID):

        command = "DELETE FROM org_subs WHERE userID = %s AND orgID = %s"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def delete_org_member(self, userID, orgID):
        
        command = "DELETE FROM org_mems WHERE userID = %s AND orgID = %s"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def delete_event_org_parent(self, eventID, orgID):
        
        command = "DELETE FROM org_mems WHERE eventID = %s AND orgID = %s"
        self.mycursor.execute(command,(eventID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result

    def get_event_subscriber(self, user_email, name,location,time):
        userID = self.get_user(user_email)[-1][-1]
        eventID = self.get_event(name,location,time)[-1][-1]

        command = "SELECT * FROM event_subs WHERE userID = %s AND eventID = %s"
        self.mycursor.execute(command,(userID,eventID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def get_org_subscriber(self, user_email, org_name):
        userID = self.get_user(user_email)[-1][-1]
        orgID = self.get_organization(org_name)[-1][-1]

        command = "SELECT * FROM org_subs WHERE userID = %s AND orgID = %s"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def get_org_member(self, user_email, org_name):
        userID = self.get_user(user_email)[-1][-1]
        orgID = self.get_organization(org_name)[-1][-1]

        command = "SELECT * FROM org_mems WHERE userID = %s AND orgID = %s"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def get_event_org_parent(self, name,location,time, org_name):
        eventID = self.get_event(name,location,time)[-1][-1]
        orgID = self.get_organization(org_name)[-1][-1]

        command = "SELECT * FROM event_parent_org WHERE eventID = %s AND orgID = %s"
        self.mycursor.execute(command,(eventID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result  

    def get_user_events(self, user_email):
        #given user email, fetches all events user is subscribed to
        userID = self.get_user(user_email)[-1][-1]
        command = "SELECT * FROM event_subs WHERE userID = %s"
        self.mycursor.execute(command,(userID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM events WHERE eventID = %s"
        events = []
        for result in results:
            self.mycursor.execute(command,(result[1],))
            tmp = self.mycursor.fetchall()
            events.append(tmp[0])
        return events  
    
    def get_event_subscribers(self, name, location, time):
        #given user email, fetches all events user is subscribed to
        eventID = self.get_event(name,location,time)[-1][-1]
        command = "SELECT * FROM event_subs WHERE eventID = %s"
        self.mycursor.execute(command,(eventID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM users WHERE userID = %s"
        users = []
        for result in results:
            self.mycursor.execute(command,(result[0],))
            tmp = self.mycursor.fetchall()
            users.append(tmp[0])
        return users
    
    def get_user_orgs(self, user_email):
        #given user email, fetches all events user is subscribed to
        userID = self.get_user(user_email)[-1][-1]
        command = "SELECT * FROM org_subs WHERE userID = %s"
        self.mycursor.execute(command,(userID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM organizations WHERE orgID = %s"
        orgs = []
        for result in results:
            self.mycursor.execute(command,(result[1],))
            tmp = self.mycursor.fetchall()
            orgs.append(tmp[0])
        return orgs

    def get_org_subscribers(self, org_name):
        #given user email, fetches all events user is subscribed to
        orgID = self.get_organization(org_name)[-1][-1]
        command = "SELECT * FROM org_subs WHERE orgID = %s"
        self.mycursor.execute(command,(orgID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM users WHERE userID = %s"
        users = []
        for result in results:
            self.mycursor.execute(command,(result[0],))
            tmp = self.mycursor.fetchall()
            users.append(tmp[0])
        return users
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
        
    def delete_event(self, name, organizationId, location, time): #assume events may have same names, eg recurring meetings
        command = "DELETE FROM events WHERE name = %s AND organizationId = %s AND location = %s AND time = %s" 
        self.mycursor.execute(command,(name,organizationId,location,time))
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

    def get_event(self, name, organizationId, location, time):
        command = "SELECT * FROM events WHERE name = %s AND organizationId = %s AND location = %s AND time = %s" 
        self.mycursor.execute(command,(name,organizationId,location,time))
        result = self.mycursor.fetchall()
        return result 

    def get_organization(self, name):
        command = "SELECT * FROM organizations WHERE name = %s" 
        self.mycursor.execute(command,(name,))
        result = self.mycursor.fetchall()
        return result 
    
    def insert_event_subscriber(self, user_email, event_details):
        userID = self.get_user(user_email)[-1]
        eventID = self.get_event(**event_details)[-1]

        command = "INSERT INTO event_subs (userID, eventID) VALUES (%d, %d)"
        self.mycursor.execute(command,(userID,eventID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def insert_org_subscriber(self, user_email, org_name):
        userID = self.get_user(user_email)[-1]
        orgID = self.get_organization(org_name)[-1]

        command = "INSERT INTO org_subs (userID, orgID) VALUES (%d, %d)"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def insert_org_member(self, user_email, org_role, org_name):
        userID = self.get_user(user_email)[-1]
        orgID = self.get_organization(org_name)[-1]

        command = "INSERT INTO org_mems (userID, orgRole, orgID) VALUES (%d, %s, %d)"
        self.mycursor.execute(command,(userID, org_role, orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def insert_event_org_parent(self, event_details, org_name):
        eventID = self.get_event(**event_details)[-1]
        orgID = self.get_organization(org_name)[-1]

        command = "INSERT INTO event_parent_org (eventID, orgID) VALUES (%d, %d)"
        self.mycursor.execute(command,(eventID, orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result

    def delete_event_subscriber(self, userID = -1, eventID = -1):
        if userID == -1 or eventID == -1:
            raise Exception("Need both keys for deletion")
        command = "DELETE FROM event_subs WHERE userID = %d AND eventID = %d" 
        self.mycursor.execute(command,(eventID, userID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def delete_org_subscriber(self, userID = -1, orgID = -1):
        if userID == -1 or orgID == -1:
            raise Exception("Need both keys for deletion")

        command = "DELETE FROM org_subs WHERE userID = %d AND orgID = %d"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def delete_org_member(self, userID = -1, orgID = -1):
        if userID == -1 or orgID == -1:
            raise Exception("Need both keys for deletion")
        
        command = "DELETE FROM org_mems WHERE userID = %d AND orgID = %d"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def delete_event_org_parent(self, eventID, orgID):
        if eventID == -1 or orgID == -1:
            raise Exception("Need both keys for deletion")
        
        command = "DELETE FROM org_mems WHERE eventID = %d AND orgID = %d"
        self.mycursor.execute(command,(eventID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result

    def get_event_subscriber(self, userID = -1, eventID = -1):
        if userID == -1 or eventID == -1:
            raise Exception("Need both keys for deletion")

        command = "SELECT FROM event_subs WHERE userID = %d AND eventID = %d"
        self.mycursor.execute(command,(userID,eventID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def get_org_subscriber(self, userID = -1, orgID = -1):
        if userID == -1 or orgID == -1:
            raise Exception("Need both keys for deletion")

        command = "SELECT FROM org_subs WHERE userID = %d AND orgID = %d"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def get_org_member(self, userID = -1, orgID = -1):
        if userID == -1 or orgID == -1:
            raise Exception("Need both keys for deletion")

        command = "SELECT FROM org_mems WHERE userID = %d AND orgID = %d"
        self.mycursor.execute(command,(userID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def get_event_org_parent(self, eventID, orgID):
        if eventID == -1 or orgID == -1:
            raise Exception("Need both keys for deletion")

        command = "SELECT FROM org_mems WHERE eventID = %d AND orgID = %d"
        self.mycursor.execute(command,(eventID,orgID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result  
    


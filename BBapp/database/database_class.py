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

    def insert_organization(self, name, email, password): #enforce unique names
        command = "INSERT INTO organizations (name, email, password) VALUES (%s, %s, %s)" 
        self.mycursor.execute(command,(name,email,password))
        result = self.mycursor.fetchall() #incase later we want to see results
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
    
    


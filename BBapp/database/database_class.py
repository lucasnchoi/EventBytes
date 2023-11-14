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
    
    def get_event_by_id(self, eventID):
        command = "SELECT * FROM events WHERE eventID = %s" 
        self.mycursor.execute(command,(eventID,))
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

    def insert_event_subscriber(self, userID, eventID):

        command = "INSERT INTO event_subs (userID, eventID) VALUES (%s, %s)"
        self.mycursor.execute(command,(userID,eventID))
        result = self.mycursor.fetchall()
        self.mydb.commit()
        return result
    
    def get_user_subscribed_events(self, userID):

        command = "SELECT * FROM event_subs WHERE userID = %s"
        self.mycursor.execute(command,(userID,))
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

    def get_event_subscriber(self, userID, eventID):

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
        #given event details, fetches all users subscribed to event
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
    
    def get_user_org_subs(self, user_email):
        #given user email, fetches all orgs user is subscribed to
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
        #given org name, fetches all users subscribed to org
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
    
    def get_user_org_memberships(self, user_email):
        #given user email, fetches all orgs user is a member of
        userID = self.get_user(user_email)[-1][-1]
        command = "SELECT * FROM org_mems WHERE userID = %s"
        self.mycursor.execute(command,(userID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM organizations WHERE orgID = %s"
        orgs = []
        for result in results:
            self.mycursor.execute(command,(result[2],))
            tmp = self.mycursor.fetchall()
            orgs.append(tmp[0])
        return orgs

    def get_org_memberships(self, org_name):
        #given org name, fetches all users that are members of the org
        orgID = self.get_organization(org_name)[-1][-1]
        command = "SELECT * FROM org_mems WHERE orgID = %s"
        self.mycursor.execute(command,(orgID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM users WHERE userID = %s"
        users = []
        for result in results:
            self.mycursor.execute(command,(result[0],))
            tmp = self.mycursor.fetchall()
            users.append(tmp[0])
        return users
    
    def get_event_org(self, name, location, time):
        #given event details, fetches org event belongs to
        eventID = self.get_event(name, location, time)[-1][-1]
        command = "SELECT * FROM event_parent_org WHERE eventID = %s"
        self.mycursor.execute(command,(eventID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM organizations WHERE orgID = %s"
        orgs = []
        for result in results:
            self.mycursor.execute(command,(result[1],))
            tmp = self.mycursor.fetchall()
            orgs.append(tmp[0])
        return orgs
    
    def get_org_events(self, org_name):
        #given org name, fetches all events for the organization
        orgID = self.get_organization(org_name)[-1][-1]
        command = "SELECT * FROM event_parent_org WHERE orgID = %s"
        self.mycursor.execute(command,(orgID,))
        results = self.mycursor.fetchall()
        command = "SELECT * FROM events WHERE eventID = %s"
        events = []
        for result in results:
            self.mycursor.execute(command,(result[0],))
            tmp = self.mycursor.fetchall()
            users.append(tmp[0])
        return users
    
    def force_reconnect(self):
        self.mydb.reconnect()

        #events.append(tmp[0])
        #return events
    
    def search_events(self, user_query, for_sub, current_time):
        # user_query can be either event name, organization name or location as indicated by user in the search bar
        command = """
        SELECT e.*
        FROM events e
        LEFT JOIN organizations o ON e.organizationId = o.orgID
        WHERE (e.name LIKE %s OR o.name LIKE %s OR e.location LIKE %s) AND e.time > %s 
        ORDER BY time
        """
        #for displaying search results of My_Events on dashboard
        command_sub = """
        SELECT e.*
        FROM events e
        LEFT JOIN organizations o ON e.organizationId = o.orgID JOIN event_subs s ON e.eventId = s.eventID
        WHERE (e.name LIKE %s OR o.name LIKE %s OR e.location LIKE %s) AND e.time > %s 
        ORDER BY time
        """

        if for_sub:
            self.mycursor.execute(command_sub,(user_query, user_query, user_query, current_time))
        else:
            self.mycursor.execute(command,(user_query, user_query, user_query, current_time))
        

        searched_events = self.mycursor.fetchall()
        return searched_events


    def search_UserEvents(self, user_query, userId):

        command = """
        SELECT * 
        FROM events e
        LEFT JOIN organizations o ON e.organizationId = o.orgID
        WHERE (e.name LIKE %s OR o.name LIKE %s OR e.location LIKE %s) AND e.creatorId = %s
        ORDER BY time
        """
        self.mycursor.execute(command,(user_query, user_query, user_query, userId))

        searched_userEvents = self.mycursor.fetchall()
        return searched_userEvents


    def filter_events_byDate(self, start_date, end_date, for_sub, current_time):
        
        command = """
        SELECT *
        FROM events
        WHERE (time BETWEEN %s AND %s) AND e.time > %s 
        ORDER BY time ASC;
        """

        command_sub = """
        SELECT *
        FROM events 
        JOIN event_subs ON events.eventId = event_subs.eventID
        WHERE (time BETWEEN %s AND %s) AND e.time > %s
        ORDER BY time ASC;
        """

        if for_sub:
            self.mycursor.execute(command_sub,(start_date, end_date, current_time))
        else:
            self.mycursor.execute(command,(start_date, end_date, current_time))

        filtered_events = self.mycursor.fetchall()
        return filtered_events
    


    def filter_UserEvents_byDate(self, start_date, end_date, userId):

        command = """
        SELECT *
        FROM events
        WHERE (time BETWEEN %s AND %s) AND creatorId = %s 
        ORDER BY time ASC;
        """

        self.mycursor.execute(command,(start_date, end_date, userId))

        filtered_userEvents = self.mycursor.fetchall()
        return filtered_userEvents
    


    def filter_event_by_type(self, filter_type, for_sub, current_time):
        
        command = "SELECT * FROM events WHERE type = %s"
        command_sub = "SELECT * FROM events LEFT JOIN event_subs ON events.eventId = event_subs.eventID WHERE type = %s AND time > %s"
        if for_sub:
            self.mycursor.execute(command_sub, filter_type, current_time)
        else:
            self.mycursor.execute(command, filter_type, current_time)

        filtered_events = self.mycursor.fetchall()
        return filtered_events
    


    def filter_UserEvent_by_type(self, filter_type, userId):
        
        command = "SELECT * FROM events WHERE type = %s AND creatorId = %s"
        self.mycursor.execute(command, (filter_type, userId))

        filtered_userEvents = self.mycursor.fetchall()
        return filtered_userEvents
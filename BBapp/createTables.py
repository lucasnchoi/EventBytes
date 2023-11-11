import mysql.connector

##Script to create tables in the database or add new columns to existing tables

db  = mysql.connector.connect(
        host="sql5.freesqldatabase.com",
        user="sql5659789",
        password="ELhaR4pm34",
        database = "sql5659789",
        port = "3306"
    )

#create table functions: 
def createUserTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS users (firstName VARCHAR(255), lastName VARCHAR(255), email VARCHAR(255), phone VARCHAR(255), password VARCHAR(255), orgID INT, orgRole VARCHAR(255), userID INT AUTO_INCREMENT PRIMARY KEY)")

def createEventTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS events (name VARCHAR(255), type VARCHAR(255), location VARCHAR(255), time VARCHAR(255), details VARCHAR(255), booking VARCHAR(255), accommodation VARCHAR(255), requisite VARCHAR(255), size INT, contact VARCHAR(255), organizationId INT, creatorId INT, eventId INT AUTO_INCREMENT PRIMARY KEY)")

def createOrganizationTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS organizations (name VARCHAR(255), email VARCHAR(255), description VARCHAR(255), organization_type VARCHAR(255), password VARCHAR(255), orgID INT AUTO_INCREMENT PRIMARY KEY)")

def createEventSubscriberTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS event_subs (userID INT, eventID INT, ESID INT AUTO_INCREMENT PRIMARY KEY)")

def createOrgSubscribersTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS org_subs (userID INT, orgID INT, OSID INT AUTO_INCREMENT PRIMARY KEY)")

def createOrgMembersTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS org_mems (userID INT, orgRole VARCHAR(255), orgID INT, OMID INT AUTO_INCREMENT PRIMARY KEY)")

def createEventParentOrgTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS event_parent_org (eventID INT, orgID INT, EPOID INT AUTO_INCREMENT PRIMARY KEY)")

def create_all_tables():
    createUserTable()
    createEventTable()
    createOrganizationTable()
    createEventSubscriberTable()
    createOrgSubscribersTable()
    createOrgMembersTable()
    createEventParentOrgTable()

#drop table functions:

def deleteUserTable():
    mycursor = db.cursor()
    mycursor.execute("DROP TABLE IF EXISTS users")

def deleteEventTable():
    mycursor = db.cursor()
    mycursor.execute("DROP TABLE IF EXISTS events")

def deleteOrganizationTable():
    mycursor = db.cursor()
    mycursor.execute("DROP TABLE IF EXISTS organizations")

def deleteEventSubscriberTable():
    mycursor = db.cursor()
    mycursor.execute("DROP TABLE IF EXISTS event_subs")

def deleteOrgSubscribersTable():
    mycursor = db.cursor()
    mycursor.execute("DROP TABLE IF EXISTS org_subs")

def deleteOrgMembersTable():
    mycursor = db.cursor()
    mycursor.execute("DROP TABLE IF EXISTS org_mems")

def deleteEventParentOrgTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS event_parent_org (eventID INT, orgID INT, EPOID INT AUTO_INCREMENT PRIMARY KEY)")

def delete_all_tables():
    deleteUserTable()
    deleteEventTable()
    deleteOrganizationTable()
    deleteEventSubscriberTable()
    deleteOrgSubscribersTable()
    deleteOrgMembersTable()
    deleteEventParentOrgTable()

def reset_tables():
    delete_all_tables()
    create_all_tables()

    

if __name__ == '__main__':
    reset_tables()



    
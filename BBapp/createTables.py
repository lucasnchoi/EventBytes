import mysql.connector

##Script to create tables in the database or add new columns to existing tables

db  = mysql.connector.connect(
        host="sql5.freesqldatabase.com",
        user="sql5659789",
        password="ELhaR4pm34",
        database = "sql5659789",
        port = "3306"
    )

def createUserTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS users (firstName VARCHAR(255), lastName VARCHAR(255), email VARCHAR(255), phone VARCHAR(255), password VARCHAR(255), orgID INT, orgRole VARCHAR(255), userID INT AUTO_INCREMENT PRIMARY KEY)")

def createEventTable():
    mycursor = db.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS events (name VARCHAR(255), type VARCHAR(255), location VARCHAR(255), time VARCHAR(255), details VARCHAR(255), booking VARCHAR(255), accommodation VARCHAR(255), requisite VARCHAR(255), size INT, contact VARCHAR(255), organizationId INT, creatorId INT, eventId INT AUTO_INCREMENT PRIMARY KEY)")
    pass

def createOrganizationTable():
    pass

if __name__ == '__main__':
    createUserTable()
    createEventTable()
    createOrganizationTable()


    
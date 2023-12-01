from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import string
import random


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)



def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patient WHERE Username = %s"
    
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            print (row['Username'])
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return
    
    if len(tokens) != 3:
        print("Login failed.")
        return
    
    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return
    
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient



def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver

def printCommand():
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
        print("> logout")  # // TODO: implement logout (Part 2)
        print("> Quit")
        print()
        return
    
def search_caregiver_schedule(tokens):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print("Please try again! You need to enter a date.")
        return
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

        #Check if date is in the format of mm-dd-yyyy
    if len(date_tokens) != 3:
        print("Please try again! You need to enter a date in the format mm-dd-yyyy.")
        return
    elif month > 12 or month < 1:
        print("Please try again! You entered an invalid month.")
        return
    elif day > 31 or day < 1:
        print("Please try again! You entered an invalid day.")
        return
    elif year < 2023:
        print("Please try again! You entered an invalid year.")
        return
    

    search_schedule = "SELECT Username FROM Availabilities WHERE TIME = %s"
    search_vaccine = "SELECT * FROM Vaccines WHERE Doses > 0"
    try:
        cursor.execute(search_schedule, d)
        print("Caregivers Available:")
        for row in cursor:
            print(row)
        print('\n')
        cursor.execute(search_vaccine)
        print("Vaccines Available:")
        for row in cursor:
            print(row)
    except pymssql.Error:
            print("Please try again! Database error occurred.")
            return
    finally:
            cm.close_connection()
    

def reserve(tokens):
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")
        return
    #extract date and vaccine from tokens
    if len(tokens) != 3:
        print("Please try again! You need to enter a date and vaccine.")
        return
    date = tokens[1]
    vaccine = tokens[2]

    #Check if date includes hyphen, if not, print error
    if date.find("-") == -1:
        print("Please try again! You need to enter a date in the format mm-dd-yyyy.")
        return
     # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    #Check if date is in the format of mm-dd-yyyy
    if len(date_tokens) != 3:
        print("Please try again! You need to enter a date in the format mm-dd-yyyy.")
        return
    elif month > 12 or month < 1:
        print("Please try again! You entered an invalid month.")
        return
    elif day > 31 or day < 1:
        print("Please try again! You entered an invalid day.")
        return
    elif year < 2023:
        print("Please try again! You entered an invalid year.")
        return
    
    #Check if date is in the past
    if datetime.datetime(year, month, day) < datetime.datetime.now():
        print("Please try again! You entered a date in the past.")
        return
    
    d = datetime.datetime(year, month, day)
    #check if there are available caregivers at that time
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    search_schedule = "SELECT Username FROM Availabilities WHERE TIME = %s ORDER BY Username ASC"
    try:
        cursor.execute(search_schedule, d)
        if cursor.rowcount == 0:
            print("No caregivers available at that time.")
            return
        #Extract the first row of the cursor
        row = cursor.fetchone()
        caregiver = row[0]
        print("Caregiver: " + caregiver)

        #check if there are available vaccines
        search_vaccine = "SELECT Name FROM Vaccines WHERE Name = %s AND Doses > 0"
        cursor.execute(search_vaccine, vaccine)
        if cursor.rowcount == 0:
            print("Not enough available doses!")
            return
        
        #decrement the number of doses available
        decrement_vaccine = "UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = %s"
        cursor.execute(decrement_vaccine, vaccine)

        #remove the avaiability of the caregiver  of tht date on the database
        remove_availability = "DELETE FROM Availabilities WHERE Username = %s AND TIME = %s"
        cursor.execute(remove_availability, (caregiver, d))

        #generate a 5 digit appointment id
        appointment_id = Util.generate_appointment_id()
        print("Appointment ID: " + appointment_id)
        
        #add the appointment to the database
        add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(add_appointment, (appointment_id, current_patient.get_username(), caregiver, d, vaccine))
        conn.commit()
        print("Appointment created!")
        print("Appointment ID: " + appointment_id + ", Caregiver Username: " + caregiver)
    except pymssql.Error:
            print("Please try again! Database error occurred.")
            return
    
    finally:
            cm.close_connection()

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    global current_patient
    global current_caregiver

    if len(tokens) != 1:
        print("Number of Argument Incorrect. Please try again!")
        return
    
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    #if the current user is a patient, fetch all appointments for that patient
    if current_patient is not None:
        search_appointments = "SELECT Appointmet_ID , Vaccine_Name, Time, Patient_Username FROM Appointments WHERE Patient_Username = %s ORDER BY Appointmet_ID ASC"
        print("Fetching Appointment for" + current_patient.get_username())

        try:
            cursor.execute(search_appointments, current_patient.get_username())
            print("Appointments:")
            for row in cursor:
                print(row)
        except pymssql.Error:
            print("Please try again! Database error occurred.")
            return
        finally:
            cm.close_connection()
            return
        
    #if the current user is a caregiver, fetch all appointments for that caregiver
    if current_caregiver is not None:
        search_appointments = "SELECT Appointmet_ID , Vaccine_Name, Time, Caregiver_Username FROM Appointments WHERE Caregiver_Username = %s ORDER BY Appointmet_ID ASC"
        print("Fetching Appointment for " + current_caregiver.get_username())
        try:
            cursor.execute(search_appointments, current_caregiver.get_username())
            print("Appointments:")
            for row in cursor:
                print(row)
        except pymssql.Error:
            print("Please try again! Database error occurred.")
            return
        finally:
            cm.close_connection()
            return


def logout(tokens):
    #If user is not logged in, print Please Login First
    if len(tokens) != 1:
        print("Number of Argument Incorrect. Please try again!")
        return
    
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    #If user is logged in, print Successfully Logged Out
    if current_patient is not None :
        current_patient = None
        print("Successfully Logged Out")
        return
    if current_caregiver is not None :
        current_caregiver = None
        print ("Successfully Logged Out")
        return


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
            printCommand()
            
        elif operation == "create_caregiver":
            create_caregiver(tokens)
            printCommand()

        elif operation == "login_patient":
            login_patient(tokens)
            printCommand()

        elif operation == "login_caregiver":
            login_caregiver(tokens)
            printCommand()

        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
            printCommand()
        elif operation == "reserve":
            reserve(tokens)
            printCommand()
        elif operation == "upload_availability":
            upload_availability(tokens)
            printCommand()
        elif operation == cancel:
            cancel(tokens)
            printCommand()
        elif operation == "add_doses":
            add_doses(tokens)
            printCommand()
        elif operation == "show_appointments":
            show_appointments(tokens)
            printCommand()
        elif operation == "logout":
            logout(tokens)
            printCommand()
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()

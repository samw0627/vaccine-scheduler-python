import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


class Vaccine:
    def __init__(self, vaccine_name, available_doses):
        self.vaccine_name = vaccine_name
        self.available_doses = available_doses

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
    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_vaccine = "SELECT Name, Doses FROM Vaccines WHERE Name = %s"
        try:
            cursor.execute(get_vaccine, self.vaccine_name)
            for row in cursor:
                self.available_doses = row[1]
                return self
        except pymssql.Error:
            print("Error occurred when getting Vaccine")
            raise
        finally:
            cm.close_connection()
        return None

    def get_vaccine_name(self):
        return self.vaccine_name

    def get_available_doses(self):
        return self.available_doses

    def save_to_db(self):
        if self.available_doses is None or self.available_doses <= 0:
            raise ValueError("Argument cannot be negative!")

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_doses = "INSERT INTO VACCINES VALUES (%s, %d)"
        try:
            cursor.execute(add_doses, (self.vaccine_name, self.available_doses))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when insert Vaccines")
            raise
        finally:
            cm.close_connection()

    # Increment the available doses
    def increase_available_doses(self, num):
        if num <= 0:
            raise ValueError("Argument cannot be negative!")
        self.available_doses += num

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        update_vaccine_availability = "UPDATE vaccines SET Doses = %d WHERE name = %s"
        try:
            cursor.execute(update_vaccine_availability, (self.available_doses, self.vaccine_name))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when updating vaccine availability")
            raise
        finally:
            cm.close_connection()

    # Decrement the available doses
    def decrease_available_doses(self, num):
        if self.available_doses - num < 0:
            ValueError("Not enough available doses!")
        self.available_doses -= num

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        update_vaccine_availability = "UPDATE vaccines SET Doses = %d WHERE name = %s"
        try:
            cursor.execute(update_vaccine_availability, (self.available_doses, self.vaccine_name))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when updating vaccine availability")
            raise
        finally:
            cm.close_connection()

    def __str__(self):
        return f"(Vaccine Name: {self.vaccine_name}, Available Doses: {self.available_doses})"

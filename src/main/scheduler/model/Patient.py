import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql

class Patient:
      def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

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
        cursor = conn.cursor(as_dict=True)

        get_patient_details = "SELECT Salt, Hash FROM Patient WHERE Username = %s"
        try:
            cursor.execute(get_patient_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None
        

      def get_username(self):
        return self.username

      def get_salt(self):
        return self.salt

      def get_hash(self):
        return self.hash
        
      def save_to_db(self):
            cm = ConnectionManager()
            conn = cm.create_connection()
            cursor = conn.cursor()

            add_patients = "INSERT INTO Patient VALUES (%s, %s, %s)"
            try:
                cursor.execute(add_patients, (self.username, self.salt, self.hash))
                conn.commit()

            except pymssql.Error as e:
                raise e
            finally:
                cm.close_connection()

    

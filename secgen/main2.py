import json
from csv import Error
import sqlite3
from enum import Enum, IntEnum
import random
import hashlib
from datetime import datetime
from pydantic import BaseModel, ConfigDict, ValidationError




class Permissions(Enum):
    ADMIN = 0
    DEV = 3
    USER = 8
    pass

class User(BaseModel):
    username: str
    elevate: Permissions
    token: str = ''

    def __init__(self, **data):
        super().__init__(**data)
        if not self.token:
            self.token = self.generate_password()

    def generate_password(self, strength: int = 256) -> str:
        pattern = random.randbytes(strength)
        return hashlib.sha256(pattern, usedforsecurity=True).hexdigest()

class Storage():
    def __init__(self) -> None:
        self.db_path: str = "data.db"
        self._init_db()
        pass

    def _init_db(self):
        try:
            self.connect = sqlite3.connect(self.db_path)
            self.cursor = self.connect.cursor()
            self.create_table()
        except sqlite3.Error as e:
            print(f"im stupid{e}")




    def create_table(self):
        """create the table \n
        \n Example;
        table = '''\n
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                username TEXT UNIQUE ,
                elevate TEXT,
                token TEXT)
            )
        ''' """
        # So this is a placeholder
        table = '''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                username TEXT UNIQUE ,
                elevate TEXT,
                token TEXT)

        '''
        self.cursor.execute(table)
        self.connect.commit

    def get_db(self, db_path):
        self.cursor.execute("SELECT * FROM users")
        result = self.cursor.fetchall()

        for i in result:
            print(i)
            # print(result)
        return

    def get_user_by_username(self, username: str) -> User | None: # Example of a more useful getter
        if not self.cursor:
            print("Database connection not established.")
            return None
        try:
            self.cursor.execute("SELECT username, elevate, token FROM users WHERE username=?", (username,))
            row = self.cursor.fetchone()
            if row:
                # Convert stored string back to Enum member
                permission_member = Permissions[row[1]] # Assumes row[1] is 'ADMIN', 'USER', etc.
                return User(username=row[0], elevate=permission_member, token=row[2])
            return None
        except sqlite3.Error as e:
            print(f"Error fetching user {username}: {e}")
            return None
        except KeyError as e: # If string from DB doesn't match an Enum member
            print(f"Invalid permission value '{row[1]}' in DB for user {username}: {e}")
            return None

    def insert_db(self, user: User) -> int | None: # Renamed for clarity, added return type hint
        """Inserts a new user into the database."""
        insert_sql = "INSERT INTO users (timestamp, username, elevate, token) VALUES(?,?,?,?)"
        timestamp = datetime.now().isoformat()
        # Use user.elevate.name to store the string representation of the enum
        params_tuple = (timestamp, user.username, user.elevate.name, user.token)

        try:
            self.cursor.execute(insert_sql, params_tuple) # Correct way to pass parameters
            self.connect.commit() # IMPORTANT: Added ()
            return self.cursor.lastrowid # The ID of the newly inserted row

        except sqlite3.IntegrityError as e: # e.g., if username is not unique
            print(f"Could not insert user. Integrity error: {e}")
            return None
        except sqlite3.Error as e: # Catch other SQLite errors
            print(f"An SQLite error occurred: {e}")
            return None


    def close(self):
        """Closes the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connect:
            self.connect.close()
        print("Database connection closed.")


# me = User(username='love', elevate = Permissions.USER, token='')
# me2 = User(username='admin', elevate = Permissions.ADMIN, token='securepassword')
# me3 = User(username='luxa', elevate = Permissions.DEV, token='')
# me4 = User(username='testuser', elevate = Permissions.USER, token='')
# me5 = User(username='nextuser', elevate = Permissions.USER, token='')
# print(me)

# instance = Storage()
# complete = instance.get_db("data.db")
# user_id = instance.insert_db(user=me)
# user_id = instance.insert_db(user=me2)
# user_id = instance.insert_db(user=me3)
# user_id = instance.insert_db(user=me4)
# user_id = instance.insert_db(user=me5)

# print(complete)
# print(instance.__dict__)
# print(instance.get_db("data.db"))

# class Auth():

#     def __init__(self) -> None:

#         pass

#     def authenticate_user(self):
#         PartA = 'securepassword'
#         PartB = me2.token
#         print(f"part a looks like {PartA}")
#         print(f"part b looks like {PartB}")
#         if PartA is PartB:
#             print("SUCCES")
#             print(f'{PartA} and {PartB} are the same')
#         else:
#             print("FAILURE")
#             print(f'{PartA} and {PartB} are not matching')

#         # print(me)

class Auth:
    def __init__(self, storage: Storage): # Dependency Injection
        self.storage = storage

    def authenticate_user_by_token(self, username: str, token: str) -> User | None:
        try:
            user = self.storage.get_user_by_username(username)
            if user and user.token == token:
                print(f"User '{username}' authenticated successfully by token.")
                return user
            print(f"Authentication failed for user:\n'{username}'\n with provided token: \n'{token}'")

            return None
        except Exception as e:
            print('failure',e)


# a = Auth(storage=instance)

# usercheck = a.authenticate_user_by_token("admin", "securepassword")
# usercheck = a.authenticate_user_by_token("luxa", "securepassword")
def main():
        instance = Storage()
        complete = instance.get_db("data.db")
        a = Auth(storage=instance)

        usercheck = a.authenticate_user_by_token("admin", "securepassword")
        usercheck = a.authenticate_user_by_token("luxa", "securepassword")
        instance.close()
if __name__ == '__main__':
    main()

    pass

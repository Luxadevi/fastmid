import sqlite3
from venv import create
from fastapi import FastAPI, Response
from enum import Enum
from pydantic import BaseModel
from typing import Any
import hashlib
import random
from pathlib import Path
from datetime import datetime


# class Permissions(Enum):

#     ADMIN = 0
#     DEV = 3
#     USER = 8

# class User(BaseModel):
#     id: int
#     username: str
#     elevate: Permissions
#     token: str = ''
#     token2: str = "ad59c12ed4ea8cb14e4505e20750a75984a69508d5004f5cd6fe3d054a01fe68"

#     def __init__(self, **data):
#         super().__init__(**data)
#         if not self.token:
#             self.token = self.generate_password()

#     def generate_password(self, strength: int = 256) -> str:
#         pattern = random.randbytes(strength)
#         return hashlib.sha256(pattern, usedforsecurity=True).hexdigest()

#     def store_user(self, **data):
#         sqlite3



# class UserStorage(BaseModel):

#     db_path: str = "users.db"
#     conn = sqlite3.connect(self.db_path)
#     cursor = conn.cursor()

#     def __init__(self, **data):
#         super().__init__(**data)
#         if not self.create_table:
#             self.create_table = self.create_table()

#     def create_table(self, **data):
#         self.cursor.execute("""
#             CREATE TABLE IF NOT EXISTS users(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 timestamp TEXT,
#                 username TEXT,
#                 elevate TEXT,
#                 token TEXT
#             )
#         """)

#         self.conn.commit()
#         return

#     def insert_data(self, data**):
#         timestamp = datetime.now().isoformat()
#         self.cursor.execute(
#             "INSERT INTO users (timestamp, username, elevate , token) VALUES(?,?,?,?)",
#             (timestamp, username, elevate, token)
#             )
#         self.conn.commit()






# me = User(id=0 ,username = "luxa", elevate = Permissions.ADMIN)

# # print(me.__dict__)
# print(me.model_dump())
# print('-----------------------------------------------------')
# print(me.model_dump_json())

import sqlite3
from enum import Enum
from pydantic import BaseModel
import hashlib
import random
from datetime import datetime

class Permissions(Enum):
    ADMIN = 0
    DEV = 3
    USER = 8

class user(basemodel):
    username: str
    elevate: permissions
    token: str = ''
    token2: str = "ad59c12ed4ea8cb14e4505e20750a75984a69508d5004f5cd6fe3d054a01fe68"

    def __init__(self, **data):
        super().__init__(**data)
        if not self.token:
            self.token = self.generate_password()

    def generate_password(self, strength: int = 256) -> str:
        pattern = random.randbytes(strength)
        return hashlib.sha256(pattern, usedforsecurity=true).hexdigest()

# Make this a regular class, not a Pydantic model
class UserStorage:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                username TEXT UNIQUE ,
                elevate TEXT,
                token TEXT
            )
        """)
        self.conn.commit()

    def insert_user(self, user: User):
        try:
            timestamp = datetime.now().isoformat()
            self.cursor.execute(
                "INSERT INTO users (timestamp, username, elevate, token) VALUES(?,?,?,?)",
                (timestamp, user.username, user.elevate.name, user.token)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except:
            print('failure')

    def get_user(self, user_id: int):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            id, timestamp, username, elevate_str, token = result
            return User(
                id=id,
                username=username,
                elevate=Permissions[elevate_str],
                token=token
            )
        return None

    def __del__(self):
        """Close connection when object is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close()

# Example usage
me = User( username="luxa", elevate=Permissions.ADMIN)
me2 = User( username="admin", elevate=Permissions.ADMIN)
print(me.model_dump())
print('-----------------------------------------------------')
print(me.model_dump_json())
store = UserStorage()
store.insert_user(me2)
mine = store.get_user(user_id=2)
print(mine)
# user_id = storage.insert_user(me2)
# print(f"User inserted with ID: {user_id}")

# retrieved_user = storage.get_user(2)
# print("found",retrieved_user)

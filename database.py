import hashlib
import os
import sqlite3


class Database:
    def __init__(self, dbName: str) -> None:
        self.dbName = dbName

    def __enter__(self):
        self.db = sqlite3.connect(self.dbName)
        self.cursor = self.db.cursor()
        return self

    def add(self, email: str, login: str, password: str) -> None:
        """
            Adds an entry to the database. Given password should be plaintext
            it will be hashed, salted and safely stored in the table without any
            vulnerability issues.
        """
        key, salt = self.hashPlaintext(password)

        print(key.hex(), salt.hex())
        print(len(key.hex()), len(salt.hex()))

        query = f"""
            INSERT INTO Entries ('login', 'password', 'email') 
            VALUES ('{login}', '{key.hex() + salt.hex()}', '{email}')
        """

        self.cursor.execute(query)
        self.db.commit()

    def check(self, email='', login='') -> bool:
        """
            Checks if user with given email or login already exists
            in the database. Returns True/False depending on result.
        """
        user = self.cursor.execute(f"""
            SELECT login, email
            FROM Entries
            WHERE email = "{email}" OR login = "{login}"
        """).fetchone()

        return bool(user)

    def hashPlaintext(self, plaintext: str, salt=None):
        """
            Uses certain algorithms to hash and salt plaintexts such as password
            to store them safely in the database.
        """
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac(
            'sha256', plaintext.encode('utf-8'), salt, 100000)
        return key, salt

    def login(self, password: str, email='', login='') -> str:
        """
            Tries to fetch the userdata from the db, checking for data validity.
            Returns specialized str to indicate the result.
        """
        retrievedPass = self.cursor.execute(f"""
            SELECT password, login
            FROM Entries
            WHERE email = "{email}" OR login = "{login}"
        """).fetchone()

        if retrievedPass:
            key = retrievedPass[0][:64]
            salt = bytes.fromhex(retrievedPass[0][64:])
            
            if self.hashPlaintext(password, salt)[0].hex() == key:
                return True, retrievedPass[1]
            else:
                return False, 'wrong password'
        else:
            return False, 'not found'

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.db.close()
        if exc_val:
            raise

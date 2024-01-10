import os
from datetime import datetime
import sqlite3

# Extra database
QUERIES = {
    "main_db": """
        CREATE TABLE IF NOT EXISTS timeinTBL (
            "id"	INTEGER UNIQUE,
            "name"	TEXT,
            "role"	TEXT,
            "status"	TEXT,
            "amIN"	TEXT,
            "amOUT"	TEXT,
            "pmIN"	TEXT,
            "pmOUT"	TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        )
    """
}


class LocalDB:
    def __init__(self, dbName) -> None:
        self.dbName = dbName
        self.dbConnection = None
        self.cursorDesc = None
        self.rawData = None
        self.queryResults = None
        self.initDatabase()

    def initDatabase(self):
        try:
            self.executeQuery(QUERIES["main_db"], dbName=self.dbName)
        except Exception as ex:
            print(ex)

    def executeQuery(self, query=None, values=None, dbName=None):
        result = None
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            if values is not None:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            data = cursor.fetchall()
            if data is not None:
                result = data
        return result

    def insert_data(self, query, values) -> None:
        result = self.executeQuery(query, values, self.dbName)
        return result

    def retrieve_time_data(self) -> None:
        query = (
            f"SELECT name, role, status, amIN, amOUT, pmIN, pmOUT, date FROM timeinTBL"
        )
        result = self.executeQuery(query=query, dbName=self.dbName)
        return result

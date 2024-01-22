import os
from datetime import datetime
import sqlite3
import calendar
# Extra database
QUERIES = {
    "main_db":
    """
        CREATE TABLE IF NOT EXISTS timeinTBL(
        id INTEGER UNIQUE,
        name TEXT,
        role TEXT,
        tIn TEXT,
        tOut TEXT,
        date TEXT,
        day TEXT,
        month TEXT,
        year TEXT,
        remark TEXT,
        PRIMARY KEY ("id" AUTOINCREMENT))
    """,
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
        """
        Runs everytime class is instantiated, 
        """
        try:
            self.executeQuery(QUERIES["main_db"], dbName=self.dbName)
            # self.executeQuery(QUERIES["timein_db"], dbName=self.dbName)
        except Exception as ex:
            print(ex)

    def executeQuery(self, query=None, values=None, dbName=None, ret=False):
        result = None
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            if values is not None:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            
            desc = cursor.description 
            data = cursor.fetchall()

            if ret == True:
                # return result as a key:value pair dictionary
                columns = [desc[0] for desc in desc]
                queryResults = []
                for row in data:
                    queryResults.append(dict(zip(columns, row)))
                result = queryResults
            else:
                result = data
        return result

    def insert_data(self, query, values) -> None:
        result = self.executeQuery(query, values, self.dbName)
        return result

    def retrieve_time_data(self) -> None:
        """
        Query database to fetch all data
        """
        query = "SELECT * from timeinTBL"
        res = self.executeQuery(query=query, dbName=self.dbName)
        return res
    
    def retrieve_time_data2(self, name) -> None:
        """
        Query database to fetch all data
        """
        query = f"SELECT * from timeinTBL WHERE name='{name}'"
        res = self.executeQuery(query=query, dbName=self.dbName)
        return res


# DBNAME = './database/timeinout.db'
# db = LocalDB(DBNAME)
# query = "SELECT COUNT(*) FROM timeinTBL WHERE name='vinz' and date='2024-1-2' "
# res = db.executeQuery(query, dbName=DBNAME, ret=True)
# count = res[0]['COUNT(*)'] 
# print(count)
# name = 'vinz'
# date = '2024-1-2'
# col1 = 'remark'
# val1 = 'LATE'
# remark = 'INTIME'

# role = 'dev'
# tIn = '7'
# tOut = ''
# day = '1'
# month = '1'
# year = '2024'


# if count < 1:
#     print("NEW QUERY")
#     query = f"""
#     INSERT into timeinTBL (name, role, tIn, tOut, date, day, month, year, remark)
#     VALUES('{name}', '{role}', '{tIn}', '{tOut}', '{date}', '{day}', '{month}', '{year}', '{remark}')
#     """
#     res = db.executeQuery(query, dbName=DBNAME)
# else:
#     print("UPDATE QUERY")
#     query = f"""
#     UPDATE timeinTBL
#     SET {col1} = '{val1}'
#     WHERE name='{name}' and date = '{date}'
#     """
#     res = db.executeQuery(query, dbName=DBNAME)
#     # print(res)

def days_per_week(year, month):
    # Get the calendar for the given month and year
    cal = calendar.monthcalendar(year, month)

    # Initialize a list to store the days per week
    days_by_week = []

    # Iterate over the weeks in the month
    for week in cal:
        # Filter out days that belong to the previous or next month
        days_in_week = [day for day in week if day != 0]
        days_by_week.append(days_in_week)

    return days_by_week

# Example usage
year = 2024
month = 1

weeks_in_month = days_per_week(year, month)

for week_num, days_in_week in enumerate(weeks_in_month, start=1):
    print(f"Week {week_num}: {days_in_week}")


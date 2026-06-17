import mysql.connector
import os

# SQL_Manager class is for query execution, query fetching and managing MySQL connection

class SQL_Manager:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor(dictionary=True)
    
    def execute(self, query, params=None):
        self.cursor.execute(query, params)
       
    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
def managing_connection():
    connection = mysql.connector.connect(
    user=os.getenv('SQL_USER'),
    password=os.getenv('SQL_PASSWORD'),
    host='localhost',
    database='university'
    )
    return connection
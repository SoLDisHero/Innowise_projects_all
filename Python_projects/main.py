import json
import mysql.connector
import os
from dotenv import load_dotenv
from decimal import Decimal 

# Read JSON files first
# Since we use 3-4 sql,json files, we create class Loader

class Loader:
    def __init__(self, path):
        self.path = path

    def load_json(self):
        with open(self.path, "r") as file:
            return json.load(file)
        
    def load_sql(self):
        with open(self.path, "r") as file:
            return file.read()
        
rooms = Loader("data/rooms.json").load_json()
students = Loader("data/students.json").load_json()
schema = Loader("schema.sql").load_sql()

# Connect JSON files to MySQL

load_dotenv()

class SQL_Manager:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor(dictionary=True)
    
    def execute(self, query, params=None):
        self.cursor.execute(query, params)
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

connection = mysql.connector.connect(
    user=os.getenv('SQL_USER'),
    password=os.getenv('SQL_PASSWORD'),
    host='localhost',
    database='university'
)
cursor = SQL_Manager(connection)

cursor.execute("CREATE DATABASE IF NOT EXISTS university")

# ---CREATE TABLES. RUN ONCE---

# # Create rooms and students tables
# for table in schema.split(';'):
#     if table.strip():
#         cursor.execute(table)

# # Insert rooms and students JSON files
# for room in rooms:
#     cursor.execute(
#         "INSERT INTO rooms (roomid, name) VALUES (%s, %s)",
#         (room['id'], room['name'])
#     )

# for student in students:
#     birthday = student['birthday'].split('T')[0]
#     cursor.execute(
#         "INSERT INTO students (studentid, name, birthday, room, sex, roomid) VALUES (%s, %s, %s, %s, %s, %s)",
#         (student['id'], student['name'], birthday, student['room'], student['sex'], student['room'])
#     )
# cursor.commit()

# Creating class to wite our queries into JSON format instaed of using a context manager
class Writer:
    def __init__(self, path):
        self.path = path

    def export_json(self, data):
        with open(self.path, "w") as file:
            file.write(json.dumps(data, indent=4))

# ---NECESSARY QUERIES TO THE DATABASE---

# List of rooms and the number of students in each of them

req_1 = cursor.query("""
SELECT r.roomid, COUNT(s.studentid) as Num_students
FROM rooms r
LEFT JOIN students s
ON r.roomid = s.roomid
GROUP BY r.roomid
""")

# for i in req_1:
#     print(f"Rooms {i['roomid']} - Number of students {i['Num_students']}")
Writer("data_queries/json_1_result.json").export_json(req_1)

# 5 rooms with the smallest average age of students

req_2 = cursor.query("""
SELECT room, AVG(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) as age
FROM students
GROUP BY room
ORDER BY age ASC
LIMIT 5
""")

# for i in req_2:
#     print(f"Rooms {i['room']} - Average age {i['age']}")
for row in req_2: 
    for k,v in row.items():
        if isinstance(v, Decimal):
            row[k] = float(v)

Writer("data_queries/json_2_result.json").export_json(req_2)

# 5 rooms with the largest difference in the age of students

req_3 = cursor.query("""
SELECT room, MAX(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) - MIN(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) as age_difference
FROM students
GROUP BY room
ORDER BY age_difference DESC
LIMIT 5
""")

# for i in req_3:
#     print(f"Room #: {i['room']} - Age difference: {i['age_difference']}")
Writer("data_queries/json_3_result.json").export_json(req_3)

# List of rooms where different-sex students live

req_4 = cursor.query("""
SELECT room
FROM students
GROUP BY room
HAVING COUNT(DISTINCT sex) = 2
""")

# for i in req_4:
#     print(f"Room with Male and Femail in it: {i['room']}")
Writer("data_queries/json_4_result.json").export_json(req_4)

# CLOSING
cursor.close()
print("Data is successfully loaded")
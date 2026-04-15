from dotenv import load_dotenv
from decimal import Decimal 
import logging
from src.handler.loader import Loader
from src.handler.json_export import Writer
from src.db.db_conn import managing_connection, SQL_Manager
from src.handler import queries

# Create logging for event tracking instead of using print() function

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Read JSON files first

rooms = Loader("data/rooms.json").load_json()
students = Loader("data/students.json").load_json()
schema = Loader("schema.sql").load_sql()

# Create .env file

load_dotenv()

# Connect JSON files to MySQL

cursor = SQL_Manager(managing_connection())
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

# ---NECESSARY QUERIES TO THE DATABASE---

# QUERY #1: List of rooms and the number of students in each of them

req_1 = queries.rooms_students(cursor)
Writer("data_queries/json_1_result.json").export_json(req_1)
Writer("data_queries/xml_1_result.xml").export_xml(req_1)
# for i in req_1:
#     print(f"Rooms {i['roomid']} - Number of students {i['Num_students']}")

# QUERY #2: 5 rooms with the smallest average age of students

req_2 = queries.smallest_rooms_ave_age(cursor)

for row in req_2: 
    for k,v in row.items():
        if isinstance(v, Decimal):
            row[k] = float(v)

Writer("data_queries/json_2_result.json").export_json(req_2)
Writer("data_queries/xml_2_result.xml").export_xml(req_2)
# for i in req_2:
#     print(f"Rooms {i['room']} - Average age {i['age']}")

# QUERY #3: 5 rooms with the largest difference in the age of students

req_3 = queries.largest_rooms_age_diff(cursor)
Writer("data_queries/json_3_result.json").export_json(req_3)
Writer("data_queries/xml_3_result.xml").export_xml(req_3)
# for i in req_3:
#     print(f"Room #: {i['room']} - Age difference: {i['age_difference']}")

# QUERY #4: List of rooms where different-sex students live

req_4 = queries.diff_gender(cursor)
Writer("data_queries/json_4_result.json").export_json(req_4)
Writer("data_queries/xml_4_result.xml").export_xml(req_4)
# for i in req_4:
#     print(f"Room with Male and Femail in it: {i['room']}")


# CLOSING
cursor.close()
logger.info("Data is successfully loaded.")
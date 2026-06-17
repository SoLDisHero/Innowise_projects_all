# Required queries

# QUERY #1: List of rooms and the number of students in each of them
def rooms_students(cursor):
    return cursor.query("""
    SELECT r.roomid, COUNT(s.studentid) as Num_students
    FROM rooms r
    LEFT JOIN students s
    ON r.roomid = s.roomid
    GROUP BY r.roomid
    """)

# QUERY #2: 5 rooms with the smallest average age of students
def smallest_rooms_ave_age(cursor):
    return cursor.query("""
    SELECT room, AVG(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) as age
    FROM students
    GROUP BY room
    ORDER BY age ASC
    LIMIT 5
    """)

# QUERY #3: 5 rooms with the largest difference in the age of students
def largest_rooms_age_diff(cursor):
    return cursor.query("""
    SELECT room, MAX(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) - MIN(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) as age_difference
    FROM students
    GROUP BY room
    ORDER BY age_difference DESC
    LIMIT 5
    """)

# QUERY #4: List of rooms where different-sex students live
def diff_gender(cursor):
    return cursor.query("""
    SELECT room
    FROM students
    GROUP BY room
    HAVING COUNT(DISTINCT sex) = 2
    """)
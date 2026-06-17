-- Create Index for speeding up the process. Those indexes were created for practical purposes. Not all of them need to be implemented. Also, we run it once.

-- List of rooms and the number of students in each of them
CREATE INDEX i_room_student ON students (roomid);

-- 5 rooms with the smallest average age of students
CREATE INDEX i_5room ON students (room, birthday);

-- # List of rooms where different-sex students live
CREATE INDEX i_sex_room ON students (room, sex);
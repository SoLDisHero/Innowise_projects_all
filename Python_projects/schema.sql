CREATE TABLE IF NOT EXISTS rooms 
(
    roomid INT          NOT NULL,
    name VARCHAR(255)   NOT NULL,
    PRIMARY KEY (roomid)
);

CREATE TABLE IF NOT EXISTS students
(
    studentid INT       NOT NULL,
    name VARCHAR(255)   NOT NULL,
    birthday DATE       NOT NULL,
    room INT            NOT NULL,
    sex CHAR(1)         NOT NULL,
    roomid INT          NOT NULL,
    PRIMARY KEY (studentid),
    FOREIGN KEY (roomid) REFERENCES rooms (roomid)
);
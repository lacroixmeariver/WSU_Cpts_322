DROP TABLE IF EXISTS club_data;
DROP TABLE IF EXISTS input_data;
DROP TABLE IF EXISTS room_log;
DROP TABLE IF EXISTS auth;
DROP TABLE IF EXISTS email_log;

CREATE TABLE club_data (
    club_name TEXT,
    club_president TEXT,
    club_email TEXT,
    club_size INTEGER,
    club_advisor TEXT,
    club_advisor_email TEXT,
    PRIMARY KEY (club_name)
);

CREATE TABLE input_data (
    building TEXT,
    room_num INTEGER,
    times_accessed INTEGER,
    access_succeed INTEGER,
    access_fail INTEGER,
    date_entered TEXT,
    PRIMARY KEY (building, room_num, date_entered)
);

CREATE TABLE room_log (
    building TEXT,
    room_num INTEGER,
    assigned_club TEXT,
    PRIMARY KEY (assigned_club),
    FOREIGN KEY (assigned_club) REFERENCES CLUB_DATA (club_name)
);

CREATE TABLE auth (
    username TEXT,
    password_ TEXT,
    PRIMARY KEY (username)
);

CREATE TABLE email_log(
    email_id Text,
    PRIMARY KEY (email_id)
);

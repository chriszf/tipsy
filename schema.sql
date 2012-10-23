-- schema.sql

create table Users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(64),
    password VARCHAR(64),
    name VARCHAR(64)
);
create table Tasks (
    id INTEGER PRIMARY KEY,
    title VARCHAR(64),
    created_at DATETIME,
    completed_at DATETIME,
    user_id INTEGER
);

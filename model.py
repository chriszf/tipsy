"""
model.py
"""
import sqlite3

def connect_db():
    return sqlite3.connect("tipsy.db")

def new_user(db, email, password, name):          
    c = db.cursor()                                     
    query = """INSERT INTO Users VALUES (NULL, ?, ?, ?)"""                                                           
    res = c.execute(query, (email, password, name))           
    if res:
        db.commit()
        return res.lastrowid

def make_user(row):
    fields = ["id", "email", "password", "username"]
    return dict(zip(fields, row))

def authenticate(db, email, password):
    c = db.cursor()
    query = """SELECT * from Users WHERE email=? AND password=?"""
    c.execute(query, (email, password))
    result = c.fetchone()
    if result:
        fields = ["id", "email", "password", "username"]
        return make_user(result)

    return None

def get_user(db, user_id):
    """Gets a user dictionary out of the database given an id"""
    c = db.cursor()
    query = """SELECT * from Users WHERE id = ?"""
    c.execute(query, (user_id,))
    user_row = c.fetchone()
    if user_row:
        return make_user(user_row)

    return None

def new_task(db, title, user_id = None):
    """Given a title and a user_id, create a new task belonging to that user. Return the id of the created task"""
    c = db.cursor()
    query = """INSERT into Tasks values (null, ?, DATETIME('now'), null, ?)"""
    res = c.execute(query, (title, user_id))
    if res:
        db.commit()
        return res.lastrowid

def complete_task(db, task_id):
    """Mark the task with the given task_id as being complete."""
    c = db.cursor()
    query = """UPDATE Tasks SET completed_at=DATETIME('now') WHERE id=?"""
    res = c.execute(query, (task_id,))
    if res:
        db.commit()
        return res.lastrowid
    else:
        return None

def get_tasks(db, user_id=None):
    """Get all the tasks matching the user_id, getting all the tasks in the system if the user_id is not provided. Returns the results as a list of dictionaries."""
    c = db.cursor()
    if user_id:
        query = """SELECT * from Tasks WHERE user_id = ?"""
        c.execute(query, (user_id,))
    else:
        query = """SELECT * from Tasks"""
        c.execute(query)
    tasks = []
    rows = c.fetchall()
    for row in rows:
        task = make_task(row)
        tasks.append(task)

    return tasks

def get_task(db, task_id):
    """Gets a single task, given its id. Returns a dictionary of the task data."""
    c = db.cursor()
    query = """SELECT * from Tasks WHERE id = ?"""
    c.execute(query, (task_id,))
    task_row = c.fetchone()
    if task_row:
        return make_task(task_row)

    return None

def make_task(row):
    columns = ["id", "title", "created_at", "completed_at", "user_id"]
    return dict(zip(columns, row))

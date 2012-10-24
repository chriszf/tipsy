"""
model.py
"""
import sqlite3

def connect_db():
    return sqlite3.connect("tipsy.db")

def new_user(db, email, password, name):          
    c = db.cursor()                                     
    query = """INSERT INTO Users VALUES (NULL, ?, ?, ?)"""                                                           
    c.execute(query, (email, password, name))           
    db.commit()

def authenticate(db, email, password):
    c = db.cursor()
    query = """SELECT * from Users WHERE email=? AND password=?"""
    c.execute(query, (email, password))
    result = c.fetchone()
    if result:
        fields = ["id", "email", "password", "username"]
        return dict(zip(fields, result))

    return None

def get_user(db, user_id):
    """Gets a user dictionary out of the database given an id"""
    pass

def new_task(db, title, user_id):
    """Given a title and a user_id, create a new task belonging to that user. Return the id of the created task"""
    pass

def complete_task(db, task_id):
    """Mark the task with the given task_id as being complete."""
    pass

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
        task = dict(zip(["id", "title", "created_at", "completed_at", "user_id"], row))
        tasks.append(task)

    return tasks

def get_task(db, task_id):
    """Gets a single task, given its id. Returns a dictionary of the task data."""

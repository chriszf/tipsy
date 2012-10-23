"""
seed.py
"""
import model

db = model.connect_db()
user_id = model.new_user(db, "chriszf@gmail.com", "securepassword", "Christian")
task = model.new_task(db, "Complete this task list", user_id)

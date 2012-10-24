"""
tipsy.py -- A flask-based todo list
"""
from flask import Flask, render_template
import model

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", user_name="chriszf")

@app.route("/tasks")
def list_tasks():
    db = model.connect_db()
    tasks_from_db = model.get_tasks(db, None)
    return render_template("list_tasks.html", tasks=tasks_from_db)

if __name__ == "__main__":
    app.run(debug=True)

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
    return render_template("list_tasks.html")

if __name__ == "__main__":
    app.run(debug=True)

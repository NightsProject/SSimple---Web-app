from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("base.html", user="Guest", active_page="dashboard")

@app.route("/students")
def students():
    students = [
        {"id": "2023-0001", "first_name": "Alice", "last_name": "Santos", "course": "BSCS", "year": "2", "gender": "Female"},
        {"id": "2023-0002", "first_name": "John", "last_name": "Dela Cruz", "course": "BSIT", "year": "3", "gender": "Male"},
        {"id": "2023-0003", "first_name": "Maria", "last_name": "Lopez", "course": "BSEE", "year": "1", "gender": "Female"},
        {"id": "2023-0004", "first_name": "Mark", "last_name": "Reyes", "course": "BSME", "year": "4", "gender": "Male"},
        {"id": "2023-0005", "first_name": "Sophia", "last_name": "Garcia", "course": "BSN", "year": "2", "gender": "Female"},
    ]
    return render_template("students.html", students=students, active_page="students")

@app.route("/colleges")
def colleges():
    colleges = [
        {"code": "CSE", "name": "College of Computer Science and Engineering"},
        {"code": "CAS", "name": "College of Arts and Sciences"},
        {"code": "COE", "name": "College of Education"},
        {"code": "CBM", "name": "College of Business Management"},
        {"code": "CHS", "name": "College of Health Sciences"},
    ]
    return render_template("colleges.html", colleges=colleges, active_page="colleges")
from . import dashboard_bp
from flask import render_template, session, redirect, url_for

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    from datetime import datetime
    
    College = [
        {"code": "CC", "name": "College of Computing"},
        {"code": "COE", "name": "College of Engineering"},
        {"code": "CBM", "name": "College of Business and Management"},
        {"code": "CEA", "name": "College of Education and Arts"}
    ]

    Program = [
        {"code": "BSCS", "name": "Bachelor of Science in Computer Science", "college": "College of Computing"},
        {"code": "BSIT", "name": "Bachelor of Science in Information Technology", "college": "College of Computing"},
        {"code": "BSEE", "name": "Bachelor of Science in Electrical Engineering", "college": "College of Engineering"},
        {"code": "BSME", "name": "Bachelor of Science in Mechanical Engineering", "college": "College of Engineering"},
        {"code": "BSBA", "name": "Bachelor of Science in Business Administration", "college": "College of Business and Management"},
        {"code": "BSEDU", "name": "Bachelor of Secondary Education", "college": "College of Education and Arts"},
        {"code": "BFA", "name": "Bachelor of Fine Arts", "college": "College of Education and Arts"}
    ]

    Student = [
        {"name": "Anna Cruz", "program": "BSCS", "college": "College of Computing", "date_registered": datetime(2025, 10, 2)},
        {"name": "Miguel Santos", "program": "BSIT", "college": "College of Computing", "date_registered": datetime(2025, 10, 3)},
        {"name": "Liza Dela Peña", "program": "BSEE", "college": "College of Engineering", "date_registered": datetime(2025, 10, 4)},
        {"name": "Mark Villanueva", "program": "BSME", "college": "College of Engineering", "date_registered": datetime(2025, 10, 6)},
        {"name": "Carlo Reyes", "program": "BSBA", "college": "College of Business and Management", "date_registered": datetime(2025, 10, 7)},
        {"name": "Katrina Mendoza", "program": "BSEDU", "college": "College of Education and Arts", "date_registered": datetime(2025, 10, 8)},
        {"name": "Angela Ramos", "program": "BSCS", "college": "College of Computing", "date_registered": datetime(2025, 10, 9)},
        {"name": "Joshua Lim", "program": "BSEE", "college": "College of Engineering", "date_registered": datetime(2025, 10, 9)},
        {"name": "Sofia Dizon", "program": "BFA", "college": "College of Education and Arts", "date_registered": datetime(2025, 10, 10)},
        {"name": "John dela Cruz", "program": "BSIT", "college": "College of Computing", "date_registered": datetime(2025, 10, 11)},
    ]

    # --- Calculated Values ---
    total_students = len(Student)
    total_programs = len(Program)
    total_colleges = len(College)

    # Count new registrations for the current month
    now = datetime.now()
    new_registrations = sum(1 for s in Student if s["date_registered"].year == now.year and s["date_registered"].month == now.month)

    # --- Chart Data: Students per Program ---
    program_counts = {}
    for s in Student:
        program_counts[s["program"]] = program_counts.get(s["program"], 0) + 1

    program_names = list(program_counts.keys())
    program_values = list(program_counts.values())

    # --- Monthly Trend (mock example) ---
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_counts = [5, 8, 12, 6, 10, 7, 15, 18, 22, 25, 20, 19]

    # --- Recent Students (sort descending by date_registered) ---
    recent_students = sorted(Student, key=lambda s: s["date_registered"], reverse=True)[:10]

    # --- Render Template ---
    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_programs=total_programs,
        total_colleges=total_colleges,
        new_registrations=new_registrations,
        program_names=program_names,
        program_counts=program_values,
        months=months,
        monthly_counts=monthly_counts,
        recent_students=recent_students,
        username=session.get("username"),
        active_page="dashboard"
    )
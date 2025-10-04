from . import dashboard_bp
from flask import render_template, session, redirect, url_for
from .models import Dashboard

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    # Fetch data from database using Dashboard model
    stats = Dashboard.get_stats()
    program_counts_data = Dashboard.get_program_counts()
    monthly_counts = Dashboard.get_monthly_trend()
    recent_students = Dashboard.get_recent_students()
    
    # Prepare chart data
    program_names = [p['program'] for p in program_counts_data]
    program_values = [p['count'] for p in program_counts_data]

    # Months for chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # --- Render Template ---
    return render_template(
        "dashboard.html",
        total_students=stats['total_students'],
        total_programs=stats['total_programs'],
        total_colleges=stats['total_colleges'],
        new_registrations=stats['new_registrations'],
        program_names=program_names,
        program_counts=program_values,
        months=months,
        monthly_counts=monthly_counts,
        recent_students=recent_students,
        username=session.get("username"),
        active_page="dashboard"
    )

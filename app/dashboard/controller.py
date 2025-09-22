from . import dashboard_bp
from flask import render_template, session, redirect, url_for

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    return render_template('dashboard.html', username=session.get('username'))

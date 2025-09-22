from . import students_bp
from flask import render_template, session, redirect, url_for

@students_bp.route('/students')
def students():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    return render_template('students.html', username=session.get('username'))

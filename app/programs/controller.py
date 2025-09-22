from . import programs_bp
from flask import render_template, session, redirect, url_for

@programs_bp.route('/programs')
def programs():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    return render_template('programs.html', username=session.get('username'))

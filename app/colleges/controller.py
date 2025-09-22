from . import colleges_bp
from flask import render_template, session, redirect, url_for

@colleges_bp.route('/colleges')
def colleges():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    return render_template('colleges.html', username=session.get('username'))

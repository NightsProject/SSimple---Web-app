from flask import render_template, redirect, request, jsonify, url_for, flash, session
from . import user_bp
from .models import Users
from app.user.forms import RegistrationForm, LoginForm


@user_bp.route('/login', methods=['POST', 'GET'])
def login():
    """Handles user login (maps to login.html) and checks credentials against the database."""
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Users.authenticate(
            username=form.username.data, 
            password=form.password.data
        )
        
        if user:
            flash(f'Welcome back, {form.username.data}!', 'success')
            session["user_id"] = user['id']  
            session["username"] = user['username'] 
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html', form=form)

@user_bp.route('/register', methods=['POST','GET'])
def register():
    """Handles user registration (maps to signup.html)."""
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Users(email=form.email.data, password=form.password.data,username=form.username.data)
        user.add()
        flash(f'User {form.username.data} registered successfully. Please log in.', 'success')
        return redirect(url_for('.login')) # Redirect to login after registration
    else:
        return render_template('signup.html', form=form)

@user_bp.route("/delete", methods=["POST"])
def delete():
    """Handles user deletion via AJAX POST request."""
    id = request.form['id']
    if Users.delete(id):
        return jsonify(success=True,message="Successfully deleted")
    else:
        return jsonify(success=False,message="Failed")

@user_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("user.login"))
import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, request, jsonify, url_for, flash, session, current_app
from . import user_bp
from .models import Users
from app.user.forms import RegistrationForm, LoginForm, SettingsForm


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
            session["profile_picture"] = user['profile_picture']
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html', form=form)

@user_bp.route('/register', methods=['POST','GET'])
def register():
    """Handles user registration (maps to signup.html)."""
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        profile_picture_url = 'https://via.placeholder.com/36'
        if form.profile_picture.data:
            file = form.profile_picture.data
            filename = secure_filename(file.filename)
            unique_filename = f"{os.urandom(8).hex()}_{filename}"
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', unique_filename)
            file.save(file_path)
            profile_picture_url = url_for('static', filename=f'uploads/{unique_filename}')

        user = Users(email=form.email.data, password=form.password.data, username=form.username.data, profile_picture=profile_picture_url)
        user.add()
        flash(f'User {form.username.data} registered successfully. Please log in.', 'success')
        return redirect(url_for('.login')) # Redirect to login after registration
    return render_template('signup.html', form=form)

@user_bp.route("/delete", methods=["POST"])
def delete():
    """Handles user deletion via AJAX POST request."""
    id = request.form['id']
    if Users.delete(id):
        return jsonify(success=True,message="Successfully deleted")
    else:
        return jsonify(success=False,message="Failed")

@user_bp.route("/settings", methods=['GET', 'POST'])
def settings():
    """Handles user settings page."""
    if 'user_id' not in session:
        flash('Please log in to access settings.', 'warning')
        return redirect(url_for('.login'))

    form = SettingsForm()
    user_id = session['user_id']

    if request.method == 'GET':
        # Populate form with current user data
        user_data = Users.get_user_with_info(user_id)
        if user_data:
            form.username.data = user_data.get('username')
            form.email.data = user_data.get('email')
            form.fullname.data = user_data.get('fullname')
            form.address.data = user_data.get('address')
            if user_data.get('birthday'):
                form.birthday.data = user_data.get('birthday')

    if request.method == 'POST' and form.validate_on_submit():
        profile_picture_url = session.get('profile_picture', 'https://via.placeholder.com/36')
        if form.profile_picture.data:
            file = form.profile_picture.data
            filename = secure_filename(file.filename)
            unique_filename = f"{os.urandom(8).hex()}_{filename}"
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', unique_filename)
            file.save(file_path)
            profile_picture_url = url_for('static', filename=f'uploads/{unique_filename}')

        # Handle password change
        password_updated = False
        if form.current_password.data and form.new_password.data:
            user_data = Users.authenticate(session['username'], form.current_password.data)
            if user_data:
                # Hash new password
                import hashlib
                hashed_password = hashlib.md5(form.new_password.data.encode()).hexdigest()
                Users.update_password(user_id, hashed_password)
                password_updated = True
            else:
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('.settings'))

        # Update user data
        Users.update_user(user_id, {
            'username': form.username.data,
            'email': form.email.data,
            'profile_picture': profile_picture_url
        })

        Users.update_user_info(user_id, {
            'fullname': form.fullname.data,
            'address': form.address.data,
            'birthday': form.birthday.data
        })

        # Update session
        session['username'] = form.username.data
        session['profile_picture'] = profile_picture_url

        success_message = 'Settings updated successfully!'
        if password_updated:
            success_message += ' Password has been changed.'
        flash(success_message, 'success')
        return redirect(url_for('.settings'))

    return render_template('settings.html', form=form)

@user_bp.route("/about")
def about():
    """About Us page."""
    return render_template('about.html')

@user_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("user.login"))

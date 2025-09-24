from . import colleges_bp
from flask import render_template, session, redirect, url_for, request, flash
from . import models
from .forms import CollegeForm


@colleges_bp.route('/colleges')
def colleges():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    form = CollegeForm()
    #college
    
    return render_template('colleges.html', form=form, username=session.get('username'))


@colleges_bp.route("/colleges/add", methods=["POST"])
def add_college():
    form = CollegeForm()

    if form.validate_on_submit():
        code = form.code.data
        name = form.name.data
        try:
            #Insert college to DB
            
            flash(f"College '{name}' added successfully!", "success")
            return redirect(url_for("colleges.colleges"))
        except Exception as e:
            flash("Database error: " + str(e), "danger")
            return render_template("colleges.html", form=form, show_modal=True)
    else:
        flash("Failed to add college. Please check the form fields.", "danger")
        return render_template("colleges.html", form=form, show_modal=True)
    
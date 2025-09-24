from . import colleges_bp
from flask import render_template, session, redirect, url_for, request, flash
from .models import Colleges
from .forms import CollegeForm


@colleges_bp.route('/colleges')
def list():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    college_form = CollegeForm()
    colleges_list = Colleges.get_all()
    
    return render_template('colleges.html', college_form=college_form, colleges=colleges_list, username=session.get('username'))


@colleges_bp.route("/colleges/add", methods=["POST"])
def add():
    form = CollegeForm()

    if form.validate_on_submit():
        code = form.code.data
        name = form.name.data
        try:
            Colleges(college_code=code, college_name=name).add()
            
            flash(f"College '{name}' added successfully!", "success")
            return redirect(url_for("colleges.list"))
        except Exception as e:
            flash("Database error: " + str(e), "danger")
            return render_template("colleges.html", form=form, show_modal=True)
    else:
        flash("Failed to add college. Please check the form fields.", "danger")
        return render_template("colleges.html", form=form, show_modal=True)

@colleges_bp.route("/colleges/update", methods=["POST"])
def update():
    pass

@colleges_bp.route("/colleges/delete", methods=["POST"])
def delete():
   
    code = request.form.get("code")
    if not code:
        flash("No college code provided.", "warning")
        print("No college code provided.")
        return redirect(url_for("colleges.list"))

    try:
        Colleges.delete(code)
        flash("College deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting college: {e}", "danger")
    return redirect(url_for("colleges.list"))

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

@colleges_bp.route("/colleges/update", methods=["GET", "POST"])
def update():
    
    # Use a form for validation for both GET(pre-fill) and POST(submit)
    form = CollegeForm()

    # GET: show the edit modal pre-filled
    if request.method == 'GET':
        code = request.args.get('code')
        if not code:
            flash("No college code provided.", "warning")
            return redirect(url_for('colleges.list'))

        college = Colleges.get_by_code(code)
        if not college:
            flash("College not found.", "warning")
            return redirect(url_for('colleges.list'))

        # pre-fill form
        form.code.data = college['code']
        form.name.data = college['name']

        # render the same list page but indicate we should open the edit modal
        colleges_list = Colleges.get_all()
        return render_template('colleges.html', college_form=CollegeForm(), edit_form=form, colleges=colleges_list, show_edit_modal=True, edit_code=code)

    # POST: perform update
    if request.method == 'POST':
        if form.validate_on_submit():
            original_code = request.form.get('original_code') or form.code.data
            new_code = form.code.data
            new_name = form.name.data
            try:
                updated = Colleges.update_college(original_code, new_code, new_name)
                if updated:
                    flash("College updated successfully.", "success")
                else:
                    flash("College not found or nothing changed.", "warning")
                return redirect(url_for('colleges.list'))
            except Exception as e:
                flash(f"Error updating college: {e}", "danger")
                colleges_list = Colleges.get_all()
                return render_template('colleges.html', college_form=CollegeForm(), edit_form=form, colleges=colleges_list, show_edit_modal=True, edit_code=original_code)
        else:
            flash("Please correct the errors in the form.", "danger")
            colleges_list = Colleges.get_all()
            return render_template('colleges.html', college_form=CollegeForm(), edit_form=form, colleges=colleges_list, show_edit_modal=True, edit_code=request.form.get('original_code'))

@colleges_bp.route("/colleges/delete", methods=["POST"])
def delete():
   
    code = request.form.get("code")
    if not code:
        flash("No college code provided.", "warning")
        print("No college code provided.")
        return redirect(url_for("colleges.list"))
    
    # Prevent deletion if there are programs assigned to this college
    try:
        if Colleges.has_programs(code):
            flash("Cannot delete college because there are programs assigned to it. Remove those programs first.", "warning")
            return redirect(url_for("colleges.list"))

        deleted = Colleges.delete(code)
        if deleted:
            flash("College deleted successfully.", "success")
        else:
            flash("College not found or already deleted.", "warning")
    except Exception as e:
        flash(f"Error deleting college: {e}", "danger")
    return redirect(url_for("colleges.list"))

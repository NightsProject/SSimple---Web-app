from . import students_bp
from flask import render_template, request, jsonify, session, redirect, url_for, flash
from .forms import StudentForm
from .models import Students
from ..programs.models import Programs


@students_bp.route('/students')
def students_list():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    # Get search and sort parameters
    search = request.args.get('q', '')
    sort_by = request.args.get('sort', 'id')

    # Get students list with search and sort applied
    students = Students.get_all(search=search, sort_by=sort_by)
    # prepare add/edit form and program choices so modal options are available on page load
    form = StudentForm()
    programs = Programs.get_all()
    form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]
    
    # default id_year to current year and prefill next id for that year
    try:
        from datetime import datetime
        form.id_year.data = str(datetime.now().year)
    except Exception:
        form.id_year.data = form.id_year.data or ''

    try:
        form.id_number.data = Students.get_next_id(year=form.id_year.data)
    except Exception:
        form.id_number.data = form.id_number.data or "1"

    return render_template(
        'students.html',
        username=session.get('username'),
        students=students,
        form=form,
        active_page="students"
    )


@students_bp.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """Handle adding a new student."""
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    form = StudentForm()
    
    # Populate program choices
    programs = Programs.get_all()
    form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]
    
    # Prefill next available ID for GET requests (fills gaps)
    if request.method == 'GET':
        # ensure the id_year has a default and compute next id for that year
        try:
            from datetime import datetime
            form.id_year.data = form.id_year.data or str(datetime.now().year)
        except Exception:
            form.id_year.data = form.id_year.data or ''

        try:
            form.id_number.data = Students.get_next_id(year=form.id_year.data)
        except Exception:
            form.id_number.data = form.id_number.data or "1"
    
    if form.validate_on_submit():
        student = Students(
            id_number=form.id_number.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            program_code=form.program_code.data,
            year=form.year.data,
            gender=form.gender.data
        )
        print("Form validated successfully, adding student:", student.__dict__)
        student.add()
        flash('Student added successfully!', 'success')
        return redirect(url_for('students.students_list'))
    else:
        print("Form validation failed. Errors:", form.errors)
        print("Form data:", {field.name: field.data for field in form if field.name != 'csrf_token'})
    
    return jsonify({'success': False, 'errors': form.errors}) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render_template(
        'students.html',
        form=form,
        username=session.get('username'),
        active_page="students"
    )


@students_bp.route('/students/next-id/<year>', methods=['GET'])
def next_id_for_year(year):
    """Return next student id for the requested year in JSON (e.g. 2025-0001)."""
    if 'user_id' not in session:
        return jsonify({'error': 'unauthorized'}), 401
    try:
        next_id = Students.get_next_id(year=year)
        return jsonify({'next_id': next_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@students_bp.route('/students/update', methods=['GET', 'POST'])
def update():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    # Prepare form and program choices for either GET or POST
    form = StudentForm()
    programs = Programs.get_all()
    form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]

    # GET: show the edit modal pre-filled
    if request.method == 'GET':
        id_number = request.args.get('id_number')
        if not id_number:
            flash('No student id provided.', 'warning')
            return redirect(url_for('students.students_list'))

        student = Students.get_by_id(id_number)
        if not student:
            flash('Student not found.', 'warning')
            return redirect(url_for('students.students_list'))

        # pre-fill form from student record
        form.id_number.data = student.get('id_number')
        form.first_name.data = student.get('first_name')
        form.last_name.data = student.get('last_name')
        form.program_code.data = student.get('program_code')
        form.year.data = student.get('year')
        form.gender.data = student.get('gender')

        # prepare add form separately so the page has choices for the Add modal
        add_form = StudentForm()
        add_form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]

        students_list = Students.get_all()
        return render_template(
            'students.html',
            username=session.get('username'),
            students=students_list,
            form=add_form,
            edit_form=form,
            show_edit_modal=True,
            edit_id=id_number,
            active_page="students"
        )

    # POST: perform update
    if request.method == 'POST':
        # form already has program choices set above
        # Ensure id_year is populated,
        # derive it from id_number if possible to satisfy StudentForm validators.
        if not getattr(form, 'id_year', None) or not form.id_year.data:
            id_num = request.form.get('id_number') or ''
            if id_num and '-' in id_num:
                form.id_year.data = id_num.split('-', 1)[0]
            else:
                # fallback to current year
                try:
                    from datetime import datetime
                    form.id_year.data = str(datetime.now().year)
                except Exception:
                    form.id_year.data = ''

        if form.validate_on_submit():
            original_id = request.form.get('original_id') or form.id_number.data
            try:
                updated = Students.update(
                    original_id=original_id,
                    new_id=form.id_number.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    program_code=form.program_code.data,
                    year=form.year.data,
                    gender=form.gender.data
                )
                if updated:
                    flash('Student updated successfully!', 'success')
                else:
                    flash('Student not found or nothing changed.', 'warning')
                return redirect(url_for('students.students_list'))
            except Exception as e:
                flash(f'Error updating student: {e}', 'danger')
                students_list = Students.get_all()
                # prepare add form so page has program choices
                add_form = StudentForm()
                add_form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]
                return render_template('students.html', form=add_form, edit_form=form, students=students_list, show_edit_modal=True, edit_id=original_id, username=session.get('username'), active_page="students")
        else:
            # validation failed
            flash('Please correct the errors in the form.', 'danger')
            students_list = Students.get_all()
            # prepare add form so page has program choices
            add_form = StudentForm()
            add_form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]
            return render_template('students.html', form=add_form, edit_form=form, students=students_list, show_edit_modal=True, edit_id=request.form.get('original_id'), username=session.get('username'), active_page="students")


@students_bp.route('/students/delete', methods=['POST'])
def delete_student():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    id_number = request.form.get('id_number')
    if not id_number:
        flash('No student id provided.', 'warning')
        return redirect(url_for('students.students_list'))

    try:
        deleted = Students.delete(id_number)
        if deleted:
            flash('Student deleted successfully.', 'success')
        else:
            flash('Student not found or already deleted.', 'warning')
    except Exception as e:
        flash(f'Error deleting student: {e}', 'danger')

    return redirect(url_for('students.students_list'))

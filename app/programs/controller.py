from . import programs_bp
from flask import render_template, session, redirect, url_for, request, flash
from .models import Programs
from .forms import ProgramForm
from app.colleges.models import Colleges


@programs_bp.route('/programs')
def list():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    # Get search, sort, and pagination parameters
    search = request.args.get('q', '')
    sort_by = request.args.get('sort', 'code')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Get paginated programs list with search and sort applied
    programs_data = Programs.get_all(search=search, sort_by=sort_by, page=page, per_page=per_page)
    programs_list = programs_data['items']

    program_form = ProgramForm()
    colleges_list = Colleges.get_all_list()
    # populate select choices from available colleges (no empty option)
    choices = [(c['code'], f"{c['code']} - {c['name']}") for c in colleges_list]
    program_form.college_code.choices = choices

    # Generate pagination URLs
    def url_for_page(page_num):
        args = request.args.copy()
        args['page'] = page_num
        return url_for('programs.list', **args)

    prev_url = url_for_page(page - 1) if page > 1 else None
    next_url = url_for_page(page + 1) if page < programs_data['pages'] else None

    return render_template('programs.html', program_form=program_form, programs=programs_list, colleges=colleges_list, username=session.get('username'), active_page="programs", pagination=programs_data, prev_url=prev_url, next_url=next_url)


@programs_bp.route('/programs/add', methods=['POST'])
def add():
    form = ProgramForm()
    # populate choices for validation/rendering
    colleges_list = Colleges.get_all_list()
    # if there are no colleges, user must create one first
    if not colleges_list:
        flash('No colleges available. Please add a college before creating a program.', 'warning')
        return redirect(url_for('colleges.list'))
    form.college_code.choices = [(c['code'], f"{c['code']} - {c['name']}") for c in colleges_list]

    if form.validate_on_submit():
        code = form.code.data
        name = form.name.data
        college_code = form.college_code.data
        try:
            Programs(program_code=code, program_name=name, college_code=college_code).add()
            flash(f"Program '{name}' added successfully!", "success")
            return redirect(url_for('programs.list'))
        except Exception as e:
            flash(f"Database error: {e}", "danger")
            programs_list_data = Programs.get_all()
            programs_list = programs_list_data['items']
            return render_template('programs.html', program_form=form, programs=programs_list, colleges=colleges_list, show_modal=True, pagination=programs_list_data, prev_url=None, next_url=None)
    else:
        flash("Failed to add program. Please check the form fields.", "danger")
        programs_list_data = Programs.get_all()
        programs_list = programs_list_data['items']
        return render_template('programs.html', program_form=form, programs=programs_list, colleges=colleges_list, show_modal=True, pagination=programs_list_data, prev_url=None, next_url=None)


@programs_bp.route('/programs/update', methods=['GET', 'POST'])
def update():
    # Use a form for validation for both GET (pre-fill) and POST (submit)
    colleges_list = Colleges.get_all_list()
    # require at least one college
    if not colleges_list:
        flash('No colleges available. Please add a college before editing programs.', 'warning')
        return redirect(url_for('colleges.list'))
    choices = [(c['code'], f"{c['code']} - {c['name']}") for c in colleges_list]

    form = ProgramForm()
    form.college_code.choices = choices

    # GET: show the edit modal pre-filled
    if request.method == 'GET':
        code = request.args.get('code')
        if not code:
            flash('No program code provided.', 'warning')
            return redirect(url_for('programs.list'))

        program = Programs.get_by_code(code)
        if not program:
            flash('Program not found.', 'warning')
            return redirect(url_for('programs.list'))

        # pre-fill form
        form.code.data = program['code']
        form.name.data = program['name']
        # if program has no college_code, default to first available college
        form.college_code.data = program.get('college_code') or (choices[0][0] if choices else '')

        # render the same list page but indicate we should open the edit modal
        programs_list_data = Programs.get_all()
        programs_list = programs_list_data['items']
        program_form = ProgramForm()
        program_form.college_code.choices = choices
        return render_template('programs.html', program_form=program_form, edit_form=form, programs=programs_list, colleges=colleges_list, show_edit_modal=True, edit_code=code, pagination=programs_list_data, prev_url=None, next_url=None)

    # POST: perform update
    if request.method == 'POST':
        # ensure choices set before validation
        form.college_code.choices = choices
        if form.validate_on_submit():
            original_code = request.form.get('original_code') or form.code.data
            new_code = form.code.data
            new_name = form.name.data
            college_code = form.college_code.data
            try:
                updated = Programs.update_program(original_code, new_code, new_name, college_code)
                if updated:
                    flash('Program updated successfully.', 'success')
                else:
                    flash('Program not found or nothing changed.', 'warning')
                return redirect(url_for('programs.list'))
            except Exception as e:
                flash(f'Error updating program: {e}', 'danger')
                programs_list_data = Programs.get_all()
                programs_list = programs_list_data['items']
                program_form = ProgramForm()
                program_form.college_code.choices = choices
                return render_template('programs.html', program_form=program_form, edit_form=form, programs=programs_list, colleges=colleges_list, show_edit_modal=True, edit_code=original_code, pagination=programs_list_data, prev_url=None, next_url=None)
        else:
            flash('Please correct the errors in the form.', 'danger')
            programs_list_data = Programs.get_all()
            programs_list = programs_list_data['items']
            program_form = ProgramForm()
            program_form.college_code.choices = choices
            return render_template('programs.html', program_form=program_form, edit_form=form, programs=programs_list, colleges=colleges_list, show_edit_modal=True, edit_code=request.form.get('original_code'), pagination=programs_list_data, prev_url=None, next_url=None)


@programs_bp.route('/programs/delete', methods=['POST'])
def delete():
    code = request.form.get('code')
    if not code:
        flash('No program code provided.', 'warning')
        return redirect(url_for('programs.list'))

    try:
        if Programs.has_students(code):
            flash('Cannot delete program because there are students assigned to it. Reassign or remove those students first.', 'warning')
            return redirect(url_for('programs.list'))

        deleted = Programs.delete(code)
        if deleted:
            flash('Program deleted successfully.', 'success')
        else:
            flash('Program not found or already deleted.', 'warning')
    except Exception as e:
        flash(f'Error deleting program: {e}', 'danger')

    return redirect(url_for('programs.list'))

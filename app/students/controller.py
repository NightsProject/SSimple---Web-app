from . import students_bp
from flask import render_template, request, jsonify, session, redirect, url_for, flash
from .forms import StudentForm
from .models import Students
from ..programs.models import Programs
from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_BUCKET_NAME
from supabase import create_client, Client


supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@students_bp.route('/students')
def students_list():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    # Get search, sort, pagination, and filter parameters
    search = request.args.get('q', '')
    sort_by = request.args.get('sort', 'id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    program_code_filter = request.args.get('program_code', '')
    year_filter = request.args.get('year', '')
    gender_filter = request.args.get('gender', '')

    # Get paginated students list with search, sort, and filters applied
    students_data = Students.get_all(
        search=search,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
        program_code_filter=program_code_filter if program_code_filter else None,
        year_filter=year_filter if year_filter else None,
        gender_filter=gender_filter if gender_filter else None
    )
    students = students_data['items']

    # prepare add/edit form and program choices so modal options are available on page load
    form = StudentForm()
    programs = Programs.get_all_list()
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

    # Generate pagination URLs
    def url_for_page(page_num):
        args = request.args.copy()
        args['page'] = page_num
        # Preserve filter parameters in pagination URLs
        if program_code_filter:
            args['program_code'] = program_code_filter
        if year_filter:
            args['year'] = year_filter
        if gender_filter:
            args['gender'] = gender_filter
        return url_for('students.students_list', **args)

    prev_url = url_for_page(page - 1) if page > 1 else None
    next_url = url_for_page(page + 1) if page < students_data['pages'] else None

    return render_template(
        'students.html',
        username=session.get('username'),
        students=students,
        form=form,
        active_page="students",
        pagination=students_data,
        prev_url=prev_url,
        next_url=next_url
    )


@students_bp.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """Handle adding a new student."""
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    form = StudentForm()

    # Populate program choices
    programs = Programs.get_all_list()
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
        active_page="students",
        pagination=None,
        prev_url=None,
        next_url=None
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
    form = StudentForm(prefix='edit')
    programs = Programs.get_all_list()
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
        # Extract id_year from id_number
        if '-' in id_number:
            form.id_year.data = id_number.split('-')[0]
        else:
            form.id_year.data = ''
        form.first_name.data = student.get('first_name')
        form.last_name.data = student.get('last_name')
        form.program_code.data = student.get('program_code')
        form.year.data = student.get('year')
        form.gender.data = student.get('gender')

        # prepare add form separately so the page has choices for the Add modal
        add_form = StudentForm()
        add_form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]

        students_list_data = Students.get_all()
        students_list = students_list_data['items']
        return render_template(
            'students.html',
            username=session.get('username'),
            students=students_list,
            form=add_form,
            edit_form=form,
            show_edit_modal=True,
            edit_id=id_number,
            active_page="students",
            pagination=students_list_data,
            prev_url=None,
            next_url=None
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
                students_list_data = Students.get_all()
                students_list = students_list_data['items']
                # prepare add form so page has program choices
                add_form = StudentForm()
                programs = Programs.get_all_list()
                add_form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]
                return render_template('students.html', form=add_form, edit_form=form, students=students_list, show_edit_modal=True, edit_id=original_id, username=session.get('username'), active_page="students", pagination=students_list_data, prev_url=None, next_url=None)
        else:
            # validation failed
            flash('Please correct the errors in the form.', 'danger')
            students_list_data = Students.get_all()
            students_list = students_list_data['items']
            # prepare add form so page has program choices
            add_form = StudentForm()
            programs = Programs.get_all_list()
            add_form.program_code.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]
            return render_template('students.html', form=add_form, edit_form=form, students=students_list, show_edit_modal=True, edit_id=request.form.get('original_id'), username=session.get('username'), active_page="students", pagination=students_list_data, prev_url=None, next_url=None)


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


# API Endpoints
@students_bp.route('/api/students', methods=['GET'])
def api_list_students():
    """API endpoint to list students with pagination, search, sort, and filters."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Get search, sort, pagination, and filter parameters
        search = request.args.get('q', '')
        sort_by = request.args.get('sort', 'id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        program_code_filter = request.args.get('program_code', '')
        year_filter = request.args.get('year', '')
        gender_filter = request.args.get('gender', '')

        # Get paginated students data with filters
        students_data = Students.get_all(
            search=search,
            sort_by=sort_by,
            page=page,
            per_page=per_page,
            program_code_filter=program_code_filter if program_code_filter else None,
            year_filter=year_filter if year_filter else None,
            gender_filter=gender_filter if gender_filter else None
        )

        return jsonify({
            'success': True,
            'data': students_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@students_bp.route('/api/students/<id_number>', methods=['GET'])
def api_get_student(id_number):
    """API endpoint to get a single student by ID."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        student = Students.get_by_id(id_number)
        if not student:
            return jsonify({'success': False, 'error': 'Student not found'}), 404

        return jsonify({
            'success': True,
            'data': student
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@students_bp.route('/api/students', methods=['POST'])
def api_create_student():
    """API endpoint to create a new student."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Handle both JSON and form data
        if request.content_type.startswith('multipart/form-data'):
            # Form data with file upload
            id_number = request.form.get('id_number', '').strip()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            program_code = request.form.get('program_code', '').strip()
            year = request.form.get('year')
            gender = request.form.get('gender', '').strip()
            profile_picture = request.files.get('profile_picture')
        else:
            # JSON data
            data = request.get_json()
            required_fields = ['id_number', 'first_name', 'last_name', 'program_code', 'year', 'gender']
            if not data or not all(field in data for field in required_fields):
                return jsonify({'success': False, 'error': f'Missing required fields: {", ".join(required_fields)}'}), 400

            id_number = data['id_number'].strip()
            first_name = data['first_name'].strip()
            last_name = data['last_name'].strip()
            program_code = data['program_code'].strip()
            year = data['year']
            gender = data['gender'].strip()
            profile_picture = None

        if not all([id_number, first_name, last_name, program_code, gender]) or year is None:
            return jsonify({'success': False, 'error': 'All fields must be non-empty'}), 400

        # Validate gender
        if gender not in ['Male', 'Female', 'Other']:
            return jsonify({'success': False, 'error': 'Gender must be Male, Female, or Other'}), 400

        # Check if program exists
        program = Programs.get_by_code(program_code)
        if not program:
            return jsonify({'success': False, 'error': 'Program not found'}), 404

        # Check if student already exists
        existing = Students.get_by_id(id_number)
        if existing:
            return jsonify({'success': False, 'error': 'Student with this ID already exists'}), 409

        # Validate year
        if year not in ['1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year']:
            return jsonify({'success': False, 'error': 'Year must be one of: 1st Year, 2nd Year, 3rd Year, 4th Year, 5th Year'}), 400

        # Handle profile picture upload
        file_link = None
        if profile_picture and profile_picture.filename:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in profile_picture.filename or profile_picture.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return jsonify({'success': False, 'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed.'}), 400

            # Upload to Supabase - rename file to student ID
            file_extension = profile_picture.filename.rsplit('.', 1)[1].lower()
            filename = f"{id_number}.{file_extension}"
            file_path = f"students/{filename}"

            try:
                file_bytes = profile_picture.read()
                content_type = profile_picture.mimetype
                upload_response = supabase.storage.from_(SUPABASE_BUCKET_NAME).upload(
                    path=file_path,
                    file=file_bytes,
                    file_options={"content-type": content_type}
                )


                print(upload_response)
                # Get public URL
                file_link = supabase.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(file_path)
            except Exception as upload_error:
                return jsonify({'success': False, 'error': f'File upload failed: {str(upload_error)}'}), 500

        # Create new student
        student = Students(
            id_number=id_number,
            first_name=first_name,
            last_name=last_name,
            program_code=program_code,
            year=year,
            gender=gender,
            file_link=file_link
        )
        student.add()

        return jsonify({
            'success': True,
            'message': f'Student {first_name} {last_name} created successfully',
            'data': {
                'id_number': id_number,
                'first_name': first_name,
                'last_name': last_name,
                'program_code': program_code,
                'year': year,
                'gender': gender,
                'file_link': file_link
            }
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@students_bp.route('/api/students/<id_number>', methods=['PUT'])
def api_update_student(id_number):
    """API endpoint to update a student."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Handle both JSON and form data
        if request.content_type.startswith('multipart/form-data'):
            # Form data with file upload
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            program_code = request.form.get('program_code', '').strip()
            year = request.form.get('year')
            gender = request.form.get('gender', '').strip()
            new_id = request.form.get('id_number', id_number).strip()
            profile_picture = request.files.get('profile_picture')
            clear_picture = request.form.get('clear_picture') == 'True'
        else:
            # JSON data
            data = request.get_json()
            required_fields = ['first_name', 'last_name', 'program_code', 'year', 'gender']
            if not data or not all(field in data for field in required_fields):
                return jsonify({'success': False, 'error': f'Missing required fields: {", ".join(required_fields)}'}), 400

            first_name = data['first_name'].strip()
            last_name = data['last_name'].strip()
            program_code = data['program_code'].strip()
            year = data['year']
            gender = data['gender'].strip()
            new_id = data.get('id_number', id_number).strip()
            profile_picture = None
            clear_picture = data.get('clear_picture', False)

        if not all([first_name, last_name, program_code, gender]) or year is None:
            return jsonify({'success': False, 'error': 'All fields must be non-empty'}), 400

        # Validate gender
        if gender not in ['Male', 'Female', 'Other']:
            return jsonify({'success': False, 'error': 'Gender must be Male, Female, or Other'}), 400

        # Check if program exists
        program = Programs.get_by_code(program_code)
        if not program:
            return jsonify({'success': False, 'error': 'Program not found'}), 404

        # Check if target ID already exists (if changing ID)
        if new_id != id_number:
            existing = Students.get_by_id(new_id)
            if existing:
                return jsonify({'success': False, 'error': 'Student with new ID already exists'}), 409

        # Validate year
        if year not in ['1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year']:
            return jsonify({'success': False, 'error': 'Year must be one of: 1st Year, 2nd Year, 3rd Year, 4th Year, 5th Year'}), 400

        print(profile_picture)
        # Handle profile picture upload or clearing
        file_link = None
        if clear_picture:
            # Delete existing file from Supabase if it exists
            try:
                existing_student = Students.get_by_id(id_number)
                if existing_student and existing_student.get('file_link'):
                    # Try to delete possible extensions
                    for ext in ['png', 'jpg', 'jpeg', 'gif']:
                        try:
                            supabase.storage.from_(SUPABASE_BUCKET_NAME).remove([f"students/{id_number}.{ext}"])
                        except:
                            pass  # File might not exist with this extension
            except Exception as e:
                print(f"Error deleting old file: {e}")
            # file_link remains None for clearing
        elif profile_picture and profile_picture.filename:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in profile_picture.filename or profile_picture.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return jsonify({'success': False, 'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed.'}), 400

            # Upload to Supabase - rename file to student ID
            file_extension = profile_picture.filename.rsplit('.', 1)[1].lower()
            filename = f"{new_id}.{file_extension}"
            file_path = f"students/{filename}"

            try:
                # Delete old file if exists
                try:
                    supabase.storage.from_(SUPABASE_BUCKET_NAME).remove([f"students/{id_number}.{file_extension}"])
                except:
                    pass  # Old file might not exist or different extension

                file_bytes = profile_picture.read()
                content_type = profile_picture.mimetype
                upload_response = supabase.storage.from_(SUPABASE_BUCKET_NAME).upload(
                    path=file_path,
                    file=file_bytes,
                    file_options={"content-type": content_type}
                )


                print(upload_response)
                # Get public URL
                file_link = supabase.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(file_path)
            except Exception as upload_error:
                return jsonify({'success': False, 'error': f'File upload failed: {str(upload_error)}'}), 500

        # Update student
        updated = Students.update(
            original_id=id_number,
            new_id=new_id,
            first_name=first_name,
            last_name=last_name,
            program_code=program_code,
            year=year,
            gender=gender,
            file_link=file_link,
            clear_picture=clear_picture
        )
        if updated == 0:
            return jsonify({'success': False, 'error': 'Student not found'}), 404

        return jsonify({
            'success': True,
            'message': 'Student updated successfully',
            'data': {
                'id_number': new_id,
                'first_name': first_name,
                'last_name': last_name,
                'program_code': program_code,
                'year': year,
                'gender': gender,
                'file_link': file_link
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@students_bp.route('/api/students/<id_number>', methods=['DELETE'])
def api_delete_student(id_number):
    """API endpoint to delete a student."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Delete student
        deleted = Students.delete(id_number)
        if deleted == 0:
            return jsonify({'success': False, 'error': 'Student not found'}), 404

        return jsonify({
            'success': True,
            'message': 'Student deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@students_bp.route('/api/students/next-id/<year>', methods=['GET'])
def api_next_id_for_year(year):
    """API endpoint to get next student ID for the requested year."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        next_id = Students.get_next_id(year=year)
        return jsonify({
            'success': True,
            'data': {'next_id': next_id}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

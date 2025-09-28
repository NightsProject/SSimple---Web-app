from app import db_pool
from datetime import datetime


class Students:
    def __init__(self, id_number=None, first_name=None, last_name=None, year=None, gender=None, program_code=None):
        self.id_number = id_number
        self.first_name = first_name
        self.last_name = last_name
        self.program_code = program_code
        self.year = year
        self.gender = gender

    def add(self):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO students (id_number, first_name, last_name, program_code, year_level, gender)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id_number) DO NOTHING
                    """,
                    (self.id_number, self.first_name, self.last_name, self.program_code, self.year, self.gender)
                )
                conn.commit()
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_next_id(year=None):
        """Return the next available student ID in the format YEAR-0001.

        If `year` is None, uses the current year. Only existing IDs for the
        given year are considered when filling gaps.
        """
        if year is None:
            year = datetime.now().year
        year = str(year)
        like_pattern = f"{year}-%"

        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id_number FROM students WHERE id_number LIKE %s", (like_pattern,))
                rows = cursor.fetchall()
                nums = []
                for r in rows:
                    val = r[0]
                    if not val or '-' not in val:
                        continue
                    parts = val.split('-', 1)
                    if parts[0] != year:
                        continue
                    suffix = parts[1]
                    try:
                        nums.append(int(suffix))
                    except Exception:
                        continue

                if not nums:
                    next_num = 1
                else:
                    nums = sorted(set(nums))
                    expected = 1
                    for n in nums:
                        if n > expected:
                            next_num = expected
                            break
                        if n == expected:
                            expected += 1
                    else:
                        next_num = expected

                return f"{year}-{next_num:04d}"
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_all(search=None, sort_by=None, page=1, per_page=10):
        """Return paginated students with program details joined."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                # First, get total count for pagination
                count_query = """
                    SELECT COUNT(*)
                    FROM students s
                    LEFT JOIN programs p ON s.program_code = p.program_code
                    LEFT JOIN colleges c ON p.college_code = c.college_code
                """
                count_params = []

                if search:
                    count_query += """
                    WHERE LOWER(s.id_number) LIKE LOWER(%s)
                    OR LOWER(s.first_name) LIKE LOWER(%s)
                    OR LOWER(s.last_name) LIKE LOWER(%s)
                    """
                    search_term = f"%{search}%"
                    count_params.extend([search_term, search_term, search_term])

                cursor.execute(count_query, count_params)
                total = cursor.fetchone()[0]

                # Now get paginated results
                query = """
                    SELECT s.id_number, s.first_name, s.last_name, s.program_code,
                           s.year_level, s.gender, p.program_name, c.college_name
                    FROM students s
                    LEFT JOIN programs p ON s.program_code = p.program_code
                    LEFT JOIN colleges c ON p.college_code = c.college_code
                """
                params = []

                if search:
                    query += """
                    WHERE LOWER(s.id_number) LIKE LOWER(%s)
                    OR LOWER(s.first_name) LIKE LOWER(%s)
                    OR LOWER(s.last_name) LIKE LOWER(%s)
                    """
                    params.extend([search_term, search_term, search_term])

                # Add sorting
                if sort_by:
                    sort_mapping = {
                        'id': 's.id_number',
                        'first_name': 's.first_name',
                        'last_name': 's.last_name',
                        'program': 'p.program_name',
                        'year': 's.year_level',
                        'gender': 's.gender'
                    }
                    sort_column = sort_mapping.get(sort_by, 's.id_number')
                    query += f" ORDER BY {sort_column}"
                else:
                    query += " ORDER BY s.id_number"

                # Add pagination
                offset = (page - 1) * per_page
                query += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()
                items = []
                for r in rows:
                    items.append({
                        "id_number": r[0],
                        "first_name": r[1],
                        "last_name": r[2],
                        "program_code": r[3],
                        "year": r[4],
                        "gender": r[5],
                        "program_name": r[6],
                        "college_name": r[7]
                    })

                total_pages = (total + per_page - 1) // per_page  # Ceiling division

                return {
                    'items': items,
                    'total': total,
                    'pages': total_pages,
                    'page': page,
                    'per_page': per_page
                }
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_by_id(id_number):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_number, first_name, last_name, program_code, year_level, gender 
                    FROM students WHERE id_number = %s
                    """,
                    (id_number,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return {
                    "id_number": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "program_code": row[3],
                    "year": row[4],
                    "gender": row[5]
                }
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def update(original_id, new_id, first_name, last_name, program_code, year, gender):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE students
                    SET id_number = %s, first_name = %s, last_name = %s, 
                        program_code = %s, year_level = %s, gender = %s
                    WHERE id_number = %s
                    """,
                    (new_id, first_name, last_name, program_code, year, gender, original_id)
                )
                updated = cursor.rowcount
                conn.commit()
                return updated
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def delete(id_number):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM students WHERE id_number = %s", (id_number,))
                deleted = cursor.rowcount
                conn.commit()
                return deleted
        finally:
            db_pool.putconn(conn)
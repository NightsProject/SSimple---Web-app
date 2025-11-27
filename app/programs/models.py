from app import db_pool


class Programs:
    def __init__(self, program_code=None, program_name=None, college_code=None):
        self.program_code = program_code
        self.program_name = program_name
        self.college_code = college_code

    def add(self):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO programs (program_code, program_name, college_code)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (program_code) DO NOTHING
                    """,
                    (self.program_code, self.program_name, self.college_code)
                )
                conn.commit()
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_all(search=None, sort_by=None, page=1, per_page=10):
        """Return paginated programs with college name joined."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:

                # --------------------------------------------
                # 1. COUNT QUERY
                # --------------------------------------------
                count_query = """
                    SELECT COUNT(*)
                    FROM programs p
                    LEFT JOIN colleges c ON p.college_code = c.college_code
                """
                count_params = []

                if search:
                    count_query += """
                    WHERE LOWER(p.program_code) LIKE LOWER(%s)
                    OR LOWER(p.program_name) LIKE LOWER(%s)
                    OR LOWER(c.college_name) LIKE LOWER(%s)
                    """
                    search_term = f"%{search}%"
                    count_params.extend([search_term, search_term, search_term])

                cursor.execute(count_query, count_params)
                total = cursor.fetchone()[0]

                # --------------------------------------------
                # 2. MAIN QUERY
                # --------------------------------------------
                query = """
                    SELECT p.program_code, p.program_name, p.college_code, c.college_name
                    FROM programs p
                    LEFT JOIN colleges c ON p.college_code = c.college_code
                """
                params = []

                if search:
                    query += """
                    WHERE LOWER(p.program_code) LIKE LOWER(%s)
                    OR LOWER(p.program_name) LIKE LOWER(%s)
                    OR LOWER(c.college_name) LIKE LOWER(%s)
                    """
                    params.extend([search_term, search_term, search_term])

                # --------------------------------------------
                # 3. SORTING
                # --------------------------------------------
                sort_mapping = {
                    'code': 'p.program_code',
                    'name': 'p.program_name',
                    'college_name': 'c.college_name'
                }

                sort_column = sort_mapping.get(sort_by, 'p.program_code')
                query += f" ORDER BY {sort_column}"

                # --------------------------------------------
                # 4. PAGINATION
                # --------------------------------------------
                offset = (page - 1) * per_page
                query += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # --------------------------------------------
                # 5. BUILD RESPONSE
                # --------------------------------------------
                items = []
                for r in rows:
                    items.append({
                        "code": r[0],
                        "name": r[1],
                        "college_code": r[2],
                        "college_name": r[3],
                    })

                total_pages = (total + per_page - 1) // per_page

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
    def get_by_code(program_code):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT program_code, program_name, college_code FROM programs WHERE program_code = %s",
                    (program_code,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return {"code": row[0], "name": row[1], "college_code": row[2]}
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def update_program(original_code, new_code, new_name, college_code):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE programs
                    SET program_code = %s, program_name = %s, college_code = %s
                    WHERE program_code = %s
                    """,
                    (new_code, new_name, college_code, original_code)
                )
                updated = cursor.rowcount
                conn.commit()
                return updated
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def delete(program_code):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM programs WHERE program_code = %s", (program_code,))
                deleted = cursor.rowcount
                conn.commit()
                return deleted
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_all_list():
        """Return all programs as list of dicts."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.program_code, p.program_name, p.college_code, c.college_name
                    FROM programs p
                    LEFT JOIN colleges c ON p.college_code = c.college_code
                    ORDER BY p.program_code
                    """
                )
                rows = cursor.fetchall()
                result = []
                for r in rows:
                    result.append({
                        "code": r[0],
                        "name": r[1],
                        "college_code": r[2],
                        "college_name": r[3],
                    })
                return result
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def has_students(program_code):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(1) FROM students WHERE program_code = %s", (program_code,))
                row = cursor.fetchone()
                return bool(row and row[0])
        finally:
            db_pool.putconn(conn)

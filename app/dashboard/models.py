from app import db_pool
from datetime import datetime


class Dashboard:
    @staticmethod
    def get_stats():
        """Get dashboard statistics: total students, programs, colleges, new registrations."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                # Total students
                cursor.execute("SELECT COUNT(*) FROM students")
                total_students = cursor.fetchone()[0]

                # Total programs
                cursor.execute("SELECT COUNT(*) FROM programs")
                total_programs = cursor.fetchone()[0]

                # Total colleges
                cursor.execute("SELECT COUNT(*) FROM colleges")
                total_colleges = cursor.fetchone()[0]

                # New registrations this month
                now = datetime.now()
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM students
                    WHERE EXTRACT(YEAR FROM date_registered) = %s
                    AND EXTRACT(MONTH FROM date_registered) = %s
                    """,
                    (now.year, now.month)
                )
                new_registrations = cursor.fetchone()[0]

                return {
                    'total_students': total_students,
                    'total_programs': total_programs,
                    'total_colleges': total_colleges,
                    'new_registrations': new_registrations
                }
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_program_counts():
        """Get count of students per program."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.program_name, COUNT(s.id_number) as count
                    FROM programs p
                    LEFT JOIN students s ON p.program_code = s.program_code
                    GROUP BY p.program_code, p.program_name
                    ORDER BY p.program_name
                    """
                )
                rows = cursor.fetchall()
                return [{"program": r[0], "count": r[1]} for r in rows]
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_monthly_trend():
        """Get monthly student registration trend for the current year."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXTRACT(MONTH FROM date_registered) as month,
                           COUNT(*) as count
                    FROM students
                    WHERE EXTRACT(YEAR FROM date_registered) = %s
                    GROUP BY EXTRACT(MONTH FROM date_registered)
                    ORDER BY month
                    """,
                    (datetime.now().year,)
                )
                rows = cursor.fetchall()
                # Fill in missing months with 0
                monthly_data = {i: 0 for i in range(1, 13)}
                for r in rows:
                    monthly_data[int(r[0])] = r[1]
                return list(monthly_data.values())
        finally:
            db_pool.putconn(conn)

    @staticmethod
    def get_recent_students(limit=4):
        """Get recently registered students."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT s.first_name, s.last_name, p.program_name, c.college_name, s.date_registered
                    FROM students s
                    LEFT JOIN programs p ON s.program_code = p.program_code
                    LEFT JOIN colleges c ON p.college_code = c.college_code
                    ORDER BY s.date_registered DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
                rows = cursor.fetchall()
                return [
                    {
                        "name": f"{r[0]} {r[1]}",
                        "program": r[2] or r[3],  # fallback to program_code if name is null
                        "college": r[3] or "",
                        "date_registered": r[4]
                    }
                    for r in rows
                ]
        finally:
            db_pool.putconn(conn)

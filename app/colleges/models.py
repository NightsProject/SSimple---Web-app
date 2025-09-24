from flask import g
from app import db_pool

class Colleges:
    
    def __init__(self, college_code=None, college_name=None):
        self.college_code = college_code
        self.college_name = college_name

    #new college
    def add(self):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO colleges (college_code, college_name)
                    VALUES (%s, %s)
                    ON CONFLICT (college_code) DO NOTHING
                    """,
                    (self.college_code, self.college_name)
                )
                conn.commit()
        finally:
            db_pool.putconn(conn)
        
    #read
    @staticmethod
    def get_all():
        """Read all colleges from the database and return as list of dicts"""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT college_code, college_name FROM colleges ORDER BY college_code")
                rows = cursor.fetchall()
                # Convert to list of dictionaries
                result = [{"code": r[0], "name": r[1]} for r in rows]
                return result
        finally:
            db_pool.putconn(conn)
    
    #update
    def update():
        pass
    
    #delete
    @staticmethod
    def delete(college_code):
        """Delete a college by its code"""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM colleges WHERE college_code = %s
                    """,
                    (college_code,)
                )
                conn.commit()
        finally:
            db_pool.putconn(conn)
    
    
    
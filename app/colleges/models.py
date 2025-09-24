from flask import g
from app import db_pool

class colleges:
    
    def __init__(self, college_code=None, college_name=None):
        self.college_code = college_code
        self.college_name = college_name

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
    def load():
        pass
    
    #update
    def update():
        pass
    
    #delete
    def delete():
        pass
    
    
    
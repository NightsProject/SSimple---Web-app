from flask import g
from app import db_pool
import hashlib

class Users:

    def __init__(self, username=None, password=None, email=None):
        self.username = username
        self.password = password
        self.email = email

    @classmethod
    def authenticate(cls, username, password):
        """
        Verifies a user's credentials against the PostgreSQL database
        using MD5 hashing for password comparison.
        
        Args:
            username (str): Username provided by the user.
            password (str): Plain text password provided by the user.
            
        Returns:
            dict or None: The user's details (as a dictionary) if valid, otherwise None.
        """
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, email, user_password FROM users WHERE username = %s",
                    (username,)
                )
                user_record = cursor.fetchone()
                
                if user_record:
                    # user_record structure: (id, username, email, user_password)
                    user_id, db_username, db_email, stored_password_hash = user_record
                    
                    # 2. Hash the input password using the same MD5 method used during 'add'
                    input_password_hash = hashlib.md5(password.encode()).hexdigest()
                    
                    # 3. Compare hashes
                    if input_password_hash == stored_password_hash:
                        # Return user details upon successful authentication
                        return {
                            'id': user_id,
                            'username': db_username,
                            'email': db_email
                        }

        except Exception as e:
            print(f"Authentication error: {e}")
            
        finally:
            db_pool.putconn(conn)
        
        return None 


    def add(self):
        """Add a new user to PostgreSQL using parameterized query"""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                # Use hashlib.md5 to hash the password before insertion
                cursor.execute(
                    """
                    INSERT INTO users(username, user_password, email)
                    VALUES (%s, %s, %s)
                    """,
                    (self.username, hashlib.md5(self.password.encode()).hexdigest(), self.email)
                )
                conn.commit()
        finally:
            db_pool.putconn(conn)

    @classmethod
    def all(cls):
        """Return all users, formatting results for the front-end table."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                # Select columns explicitly (id, username, email, user_password)
                cursor.execute("SELECT id, username, email, user_password FROM users") 
                result = cursor.fetchall()
                
                # Format the result as expected by index.html: (id, username, email, password_placeholder)
                formatted_results = [(row[0], row[1], row[2], '***HIDDEN***') for row in result]
                return formatted_results
        finally:
            db_pool.putconn(conn)

    @classmethod
    def delete(cls, user_id):
        """Delete a user by id and returns True if successful."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                # Check if any row was affected to confirm deletion
                return cursor.rowcount > 0 
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            db_pool.putconn(conn)

from flask import g
from app import db_pool
import hashlib

class Users:

    def __init__(self, username=None, password=None, email=None, profile_picture=None):
        self.username = username
        self.password = password
        self.email = email
        self.profile_picture = profile_picture or 'https://via.placeholder.com/36'

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
                    "SELECT id, username, email, user_password, profile_picture FROM users WHERE username = %s",
                    (username,)
                )
                user_record = cursor.fetchone()

                if user_record:
                    # user_record structure: (id, username, email, user_password, profile_picture)
                    user_id, db_username, db_email, stored_password_hash, profile_picture = user_record

                    # 2. Hash the input password using the same MD5 method used during 'add'
                    input_password_hash = hashlib.md5(password.encode()).hexdigest()

                    # 3. Compare hashes
                    if input_password_hash == stored_password_hash:
                        # Return user details upon successful authentication
                        return {
                            'id': user_id,
                            'username': db_username,
                            'email': db_email,
                            'profile_picture': profile_picture
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
                    INSERT INTO users(username, user_password, email, profile_picture)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (self.username, hashlib.md5(self.password.encode()).hexdigest(), self.email, self.profile_picture)
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

    @classmethod
    def get_user_with_info(cls, user_id):
        """Get user data along with user_info."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.username, u.email, u.profile_picture,
                           ui.fullname, ui.address, ui.birthday
                    FROM users u
                    LEFT JOIN user_info ui ON u.id = ui.user_id
                    WHERE u.id = %s
                """, (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'username': result[1],
                        'email': result[2],
                        'profile_picture': result[3],
                        'fullname': result[4],
                        'address': result[5],
                        'birthday': result[6]
                    }
        except Exception as e:
            print(f"Error getting user with info: {e}")
        finally:
            db_pool.putconn(conn)
        return None

    @classmethod
    def update_user(cls, user_id, data):
        """Update user data."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET username = %s, email = %s, profile_picture = %s
                    WHERE id = %s
                """, (data['username'], data['email'], data['profile_picture'], user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            db_pool.putconn(conn)

    @classmethod
    def update_user_info(cls, user_id, data):
        """Update or insert user_info data."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                # Check if user_info exists
                cursor.execute("SELECT id FROM user_info WHERE user_id = %s", (user_id,))
                exists = cursor.fetchone()
                if exists:
                    cursor.execute("""
                        UPDATE user_info
                        SET fullname = %s, address = %s, birthday = %s
                        WHERE user_id = %s
                    """, (data['fullname'], data['address'], data['birthday'], user_id))
                else:
                    cursor.execute("""
                        INSERT INTO user_info (fullname, address, birthday, user_id)
                        VALUES (%s, %s, %s, %s)
                    """, (data['fullname'], data['address'], data['birthday'], user_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating user info: {e}")
            return False
        finally:
            db_pool.putconn(conn)

    @classmethod
    def update_password(cls, user_id, hashed_password):
        """Update user password."""
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET user_password = %s
                    WHERE id = %s
                """, (hashed_password, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
        finally:
            db_pool.putconn(conn)

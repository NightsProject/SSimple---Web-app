import psycopg2
from psycopg2 import sql, extras
from config import DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT
from dotenv import load_dotenv

def create_database():
    
    load_dotenv('.env')
    
    
    """Connects to the default 'postgres' DB and creates DB_NAME if it doesn't exist."""
    conn = psycopg2.connect(
        dbname=DB_NAME,  
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True  # needed to create DB
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname=%s",
        (DB_NAME,)
    )
    exists = cur.fetchone()
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_NAME)
        ))
        print(f"Database '{DB_NAME}' created.")
    else:
        print(f"Database '{DB_NAME}' already exists.")
    cur.close()
    conn.close()


def get_connection():
    """Connect to the target database."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def execute_query(query, params=None):
    """Helper to execute a single query"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def ready_college_table():
    query = """
    CREATE TABLE IF NOT EXISTS colleges (
        college_code VARCHAR(20) PRIMARY KEY,
        college_name VARCHAR(100) NOT NULL
    )
    """
    execute_query(query)

def ready_program_table():
    query = """
    CREATE TABLE IF NOT EXISTS programs (
        program_code VARCHAR(20) PRIMARY KEY,
        program_name VARCHAR(100) NOT NULL,
        college_code VARCHAR(20),
        CONSTRAINT fk_college
            FOREIGN KEY (college_code)
            REFERENCES colleges(college_code)
            ON UPDATE CASCADE
            ON DELETE SET NULL
    )
    """
    execute_query(query)
 
def ready_student_table():
    query = """
    CREATE TABLE IF NOT EXISTS students (
        id_number VARCHAR(15) PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        year_level VARCHAR(20),
        gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
        program_code VARCHAR(20),
        CONSTRAINT fk_program
            FOREIGN KEY (program_code)
            REFERENCES programs(program_code)
            ON UPDATE CASCADE
            ON DELETE SET NULL
    )
    """
    execute_query(query)


def ready_year_level_table():
    query = """
    CREATE TABLE IF NOT EXISTS year_levels (
        year_level VARCHAR(20) PRIMARY KEY
    )
    """
    execute_query(query)

    insert_query = """
    INSERT INTO year_levels (year_level) VALUES %s
    ON CONFLICT (year_level) DO NOTHING
    """
    year_levels = [('1st Year',), ('2nd Year',), ('3rd Year',),
                   ('4th Year',), ('5th Year',), ('6th Year',)]
    conn = get_connection()
    cur = conn.cursor()
    try:
        extras.execute_values(cur, insert_query, year_levels)
        conn.commit()
    finally:
        cur.close()
        conn.close()


def ready_years_table():
    query = """
    CREATE TABLE IF NOT EXISTS years (
        year VARCHAR(20) PRIMARY KEY
    )
    """
    execute_query(query)

    insert_query = """
    INSERT INTO years (year) VALUES %s
    ON CONFLICT (year) DO NOTHING
    """
    years = [('2024',), ('2025',)]
    conn = get_connection()
    cur = conn.cursor()
    try:
        extras.execute_values(cur, insert_query, years)
        conn.commit()
    finally:
        cur.close()
        conn.close()

def ready_users_table():
    """Create users table with a starting sequence."""
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(20) UNIQUE,
        email VARCHAR(50),
        user_password VARCHAR(50)
    );
    """
    execute_query(query)


def ready_user_info_table():
    """Create user_info table with a starting sequence."""
    query = """
    CREATE TABLE IF NOT EXISTS user_info (
        id SERIAL PRIMARY KEY,
        fullname VARCHAR(150),
        address VARCHAR(200),
        birthday DATE,
        user_id INT REFERENCES users(id) ON DELETE CASCADE
    );
    """
    execute_query(query)


def initialize_db():
    create_database()
    ready_college_table()
    ready_program_table()
    ready_student_table()
    ready_year_level_table()
    ready_years_table()
    ready_users_table()
    ready_user_info_table()


if __name__ == '__main__':
    initialize_db()
    print("Database and tables initialized successfully.")

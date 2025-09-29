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

    insert_query = """
    INSERT INTO colleges (college_code, college_name) VALUES %s
    ON CONFLICT (college_code) DO NOTHING
    """
    colleges = [('ENG', 'College of Engineering'), ('SCI', 'College of Science'), ('ART', 'College of Arts')]
    conn = get_connection()
    cur = conn.cursor()
    try:
        extras.execute_values(cur, insert_query, colleges)
        conn.commit()
    finally:
        cur.close()
        conn.close()

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

    insert_query = """
    INSERT INTO programs (program_code, program_name, college_code) VALUES %s
    ON CONFLICT (program_code) DO NOTHING
    """
    programs = [
        ('BSCE', 'Bachelor of Science in Civil Engineering', 'ENG'),
        ('BSEE', 'Bachelor of Science in Electrical Engineering', 'ENG'),
        ('BSME', 'Bachelor of Science in Mechanical Engineering', 'ENG'),
        ('BSCS', 'Bachelor of Science in Computer Science', 'SCI'),
        ('BSMATH', 'Bachelor of Science in Mathematics', 'SCI'),
        ('BSPHY', 'Bachelor of Science in Physics', 'SCI'),
        ('BAENG', 'Bachelor of Arts in English', 'ART'),
        ('BAHIST', 'Bachelor of Arts in History', 'ART'),
        ('BAART', 'Bachelor of Arts in Fine Arts', 'ART')
    ]
    conn = get_connection()
    cur = conn.cursor()
    try:
        extras.execute_values(cur, insert_query, programs)
        conn.commit()
    finally:
        cur.close()
        conn.close()
 
def ready_student_table():
    query = """
    CREATE TABLE IF NOT EXISTS students (
        id_number VARCHAR(15) PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        year_level VARCHAR(20),
        gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
        program_code VARCHAR(20),
        date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_program
            FOREIGN KEY (program_code)
            REFERENCES programs(program_code)
            ON UPDATE CASCADE
            ON DELETE SET NULL
    )
    """
    execute_query(query)

    # Add column if not exists
    alter_query = """
    ALTER TABLE students ADD COLUMN IF NOT EXISTS date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    execute_query(alter_query)

    insert_query = """
    INSERT INTO students (id_number, first_name, last_name, year_level, gender, program_code) VALUES %s
    ON CONFLICT (id_number) DO NOTHING
    """
    first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack', 'Kate', 'Liam', 'Mia', 'Noah', 'Olivia', 'Peter', 'Quinn', 'Ryan', 'Sophia', 'Tyler', 'Uma', 'Victor', 'Wendy', 'Xander', 'Yara', 'Zoe']
    last_names = ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King']
    year_levels = ['1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year', '6th Year']
    programs = ['BSCE', 'BSEE', 'BSME', 'BSCS', 'BSMATH', 'BSPHY', 'BAENG', 'BAHIST', 'BAART']
    genders = ['Male', 'Female', 'Other']

    students = []
    for i in range(1, 131): # 130 students
        id_num = f'2024-{i:04d}'
        first_name = first_names[(i-1) % len(first_names)]
        last_name = last_names[(i-1) % len(last_names)]
        year_level = year_levels[(i-1) % len(year_levels)]
        gender = genders[(i-1) % len(genders)]
        program = programs[(i-1) % len(programs)]
        students.append((id_num, first_name, last_name, year_level, gender, program))
    conn = get_connection()
    cur = conn.cursor()
    try:
        extras.execute_values(cur, insert_query, students)
        conn.commit()
    finally:
        cur.close()
        conn.close()


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
        user_password VARCHAR(50),
        profile_picture VARCHAR(255) DEFAULT 'https://via.placeholder.com/36'
    );
    """
    execute_query(query)

    insert_query = """
    INSERT INTO users (username, email, user_password) VALUES %s
    ON CONFLICT (username) DO NOTHING
    """
    users = [
        ('admin', 'admin@example.com', 'password123'),
        ('johndoe', 'john.doe@example.com', 'pass123'),
        ('janesmith', 'jane.smith@example.com', 'pass456'),
        ('alicejohnson', 'alice.johnson@example.com', 'pass789'),
        ('bobwilliams', 'bob.williams@example.com', 'pass000')
    ]
    conn = get_connection()
    cur = conn.cursor()
    try:
        extras.execute_values(cur, insert_query, users)
        conn.commit()
    finally:
        cur.close()
        conn.close()


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

    insert_query = """
    INSERT INTO user_info (fullname, address, birthday, user_id) VALUES %s
    ON CONFLICT DO NOTHING
    """
    user_infos = [
        ('Administrator', '123 Admin St, City, Country', '1990-01-01', 1),
        ('John Doe', '456 User Ave, City, Country', '1995-05-15', 2),
        ('Jane Smith', '789 User Blvd, City, Country', '1992-08-20', 3),
        ('Alice Johnson', '101 User Rd, City, Country', '1988-12-10', 4),
        ('Bob Williams', '202 User Ln, City, Country', '1993-03-25', 5)
    ]
    conn = get_connection()
    cur = conn.cursor()
    try:
        extras.execute_values(cur, insert_query, user_infos)
        conn.commit()
    finally:
        cur.close()
        conn.close()


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

from flask import Flask, g
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT, SECRET_KEY, BOOTSTRAP_SERVE_LOCAL
from flask_wtf.csrf import CSRFProtect
from psycopg2 import pool
from flask_bootstrap import Bootstrap
import app.db_init as create_database
db_pool = None

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['SECRET_KEY'] = SECRET_KEY 
    
    CSRFProtect(app)
    Bootstrap(app)
    
    create_database.initialize_db()
    
    #Initialize connection pool ONCE
    global db_pool
    if db_pool is None:
        db_pool = pool.SimpleConnectionPool(
            1, 10,  # min/max connections
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )

    # Open connection for this request
    @app.before_request
    def get_db_connection():
        if "db_conn" not in g:
            g.db_conn = db_pool.getconn()

    # Close connection after request
    @app.teardown_appcontext
    def close_db_connection(exception):
        conn = g.pop("db_conn", None)
        if conn is not None:
            db_pool.putconn(conn)
            
            
    from .user import user_bp as user_blueprint
    app.register_blueprint(user_blueprint)
    from .dashboard import dashboard_bp as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    from .colleges import colleges_bp as colleges_blueprint
    app.register_blueprint(colleges_blueprint)
    from .programs import programs_bp as programs_blueprint
    app.register_blueprint(programs_blueprint)
    from .students import students_bp as students_blueprint
    app.register_blueprint(students_blueprint)

    return app

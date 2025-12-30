from os import getenv

SECRET_KEY = getenv("SECRET_KEY")
DB_NAME = getenv("DB_NAME")
DB_USERNAME = getenv("DB_USERNAME")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")
BOOTSTRAP_SERVE_LOCAL = getenv("BOOTSTRAP_SERVE_LOCAL")
SUPABASE_URL = getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = getenv("SUPABASE_ANON_KEY")
SUPABASE_BUCKET_NAME = getenv("SUPABASE_BUCKET_NAME", "profile-pictures")
MAX_FILE_SIZE = int(getenv("MAX_FILE_SIZE", "3145728"))  # Default restriction: 3MB in bytes (5 * 1024 * 1024)


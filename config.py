import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Konfigurasi dasar aplikasi Flask dan koneksi MySQL."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-citra-secret-key-2026')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'

    # Database settings (Laragon MySQL)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'db_mini_project_citra')

    # Uploads settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maksimum 16MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

    # Disable static file caching in browser for smooth development
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # Tesseract settings (opsional jika tesseract tidak berada di system PATH)
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', '')

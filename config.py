import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'gyh_database')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    JAKE_IMAGES_FOLDER = os.environ.get('JAKE_IMAGES_FOLDER', 'jake_images')
    MAX_IMAGE_NUMBER = int(os.environ.get('MAX_IMAGE_NUMBER', '255'))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '20'))
    MAX_SEARCH_RESULTS = int(os.environ.get('MAX_SEARCH_RESULTS', '100'))
    
    TIMEZONE = 'Asia/Jakarta'
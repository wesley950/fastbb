import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'asdf')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
DB_URL = os.getenv('DB_URL', 'sqlite:///./app.db')

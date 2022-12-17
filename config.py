import os


SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# I was unable to implement a connection to the database with this method as it gives me Operational error
# DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
# DB_USER = os.getenv('DB_USER', 'postgres')
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'natty')
# DB_NAME = os.getenv('DB_NAME', 'fyyur')

# DB_PATH = 'postgresql://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

# So i prefer to use this method as i was thought in the udacity classroom
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:natty@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuration script
# Retrieves the hidden variables from the .env
# file and creates the configuration objects -
# one for each environment.

from dotenv import load_dotenv
load_dotenv()

import os

class Config(object):
    DEBUG = False
    TESTING = False
    CORS = {
        'origins': os.getenv('CORS_ORIGINS').split(',') if os.getenv('CORS_ORIGINS') else None
    }


class ProductionConfig(Config):
    """Production configuration"""

    # TODO: add required secret configurations
    ENV='production'
    SECRET_KEY=os.getenv('PROD_SECRET_KEY')


class DevelopmentConfig(Config):
    """Development configuration"""

    # TODO: add required secret configurations
    ENV='development'
    DEBUG = True
    SECRET_KEY=os.getenv('DEV_SECRET_KEY')
    DB_USER = os.getenv('DEVELOPMENT_DATABASE_USER')
    DB_HOST = os.getenv('DEVELOPMENT_DATABASE_HOST')
    DB_PORT = os.getenv('DEVELOPMENT_DATABASE_PORT')
    DB_PASSWORD = os.getenv('DEVELOPMENT_DATABASE_PASSWORD')
    DB_NAME = os.getenv('DEVELOPMENT_DATABASE_NAME')


class TestingConfig(Config):
    """Testing configuration"""

    # TODO: add required secret configurations
    ENV='testing'
    TESTING = True
    SECRET_KEY=os.getenv('TEST_SECRET_KEY')

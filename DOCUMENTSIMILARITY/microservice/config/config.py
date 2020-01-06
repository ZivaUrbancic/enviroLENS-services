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

    # PARAMETERS FOR CONNECTING TO POSTGRES
    DATABASE_NAME=os.getenv('PROD_DATABASE_NAME')
    DATABASE_USER=os.getenv('PROD_DATABASE_USER')
    DATABASE_PASSWORD=os.getenv('PROD_DATABASE_PASSWORD')

    # Url to text embedding service
    TEXT_EMBEDDING_URL=os.getenv('PROD_TEXT_EMBEDDING_URL')

class DevelopmentConfig(Config):
    """Development configuration"""

    # TODO: add required secret configurations
    ENV='development'
    DEBUG = True
    SECRET_KEY=os.getenv('DEV_SECRET_KEY')

    # PARAMETERS FOR CONNECTING TO POSTGRES
    DATABASE_NAME=os.getenv('DEV_DATABASE_NAME')
    DATABASE_USER=os.getenv('DEV_DATABASE_USER')
    DATABASE_PASSWORD=os.getenv('DEV_DATABASE_PASSWORD')

    # Url to text embedding service
    TEXT_EMBEDDING_URL=os.getenv('DEV_TEXT_EMBEDDING_URL')


class TestingConfig(Config):
    """Testing configuration"""

    # TODO: add required secret configurations
    ENV='testing'
    TESTING = True
    SECRET_KEY=os.getenv('TEST_SECRET_KEY')

    # PARAMETERS FOR CONNECTING TO POSTGRES
    DATABASE_NAME=os.getenv('TEST_DATABASE_NAME')
    DATABASE_USER=os.getenv('TEST_DATABASE_USER')
    DATABASE_PASSWORD=os.getenv('TEST_DATABASE_PASSWORD')

    # Url to text embedding service
    TEXT_EMBEDDING_URL=os.getenv('TEST_TEXT_EMBEDDING_URL')

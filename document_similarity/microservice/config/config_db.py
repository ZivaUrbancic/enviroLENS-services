# Database config script
# Contains methods for establishing and
# closing connection with the database

from flask import current_app, g

# ! modify for different database
# import postgresql library
from ..library.postgresql import PostgresQL


def get_db():
    """Gets or establishes the connection to the database
    Returns:
        obj: The database object.
    """

    if 'db' not in g:
        # ! modify for different database
        # initialize db object
        g.db = PostgresQL()
        # get database and password for establishing the conncetion
        database = current_app.config['DATABASE_NAME']
        user = current_app.config['DATABASE_USER']
        password = current_app.config['DATABASE_PASSWORD']
        # connect to the database
        g.db.connect(database, user=user, password=password)

    # return the database connection
    return g.db


def close_db(e=None):
    """Closes the connection to the database"""

    # removes the database object from the global variable
    db = g.pop('db', None)
    if db is not None:
        # ! modify for different database
        # disconnect form the database
        db.disconnect()


def init_app(app):
    """Initializes the application and adds methods for handling the db"""
    app.teardown_appcontext(close_db)

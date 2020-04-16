# Database config script
# Contains methods for establishing and
# closing connection with the database

from flask import current_app, g
# import elasticsearch module
from elasticsearch import Elasticsearch


def get_es():
    """Gets or esablishes the connection to the database
    Returns:
        obj: The elasticsearch object.
    """

    if 'es' not in g:
        # ! modify for different database
        # initialize db object
        g.es = Elasticsearch()
    # return the database connection
    return g.es


def close_es(e=None):
    """Closes the connection to the database"""

    # removes the database object from the global variable
    es = g.pop('es', None)


def init_app(app):
    """Initializes the application and adds methods for handling the db"""
    app.teardown_appcontext(close_es)
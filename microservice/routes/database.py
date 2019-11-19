# Database routes
# Routes related with interaction with the database

import os

from flask import (
    Blueprint, flash, g, request, jsonify, current_app as app, render_template, url_for,
    Response
)
from werkzeug.exceptions import abort

from ..library import postgresql


#################################################
# Setup the database object
#################################################

DB_HOST = app.config.get('DB_HOST', 'localhost')
DB_PORT = app.config.get('DB_PORT', 5432)
DB = postgresql.PostgresQL(DB_HOST, DB_PORT)

#################################################
# Setup the index blueprint
#################################################

bp = Blueprint('database', __name__, url_prefix='/api/v1/db')

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# TODO: setup the index route
@bp.route('/', methods=['GET'])
def index():
    # get the documentation information
    # TODO: get appropriate app configurations
    HOST = app.config['HOST'] if 'HOST' in app.config else '127.0.0.1'
    PORT = app.config['PORT'] if 'PORT' in app.config else '5000'

    result = {
        "host": HOST,
        "port": PORT
    }

    # render the html file
    return render_template('index.html', result=result)

@bp.route('/document', methods=['POST'])
def get_document():
    """
    At this endpoint you get the document that you provided in the JSON body.

    JSON structure:
    {
        "document_id" : (id of the document)
    }

    The function returns a JSON response with the data of the document.
    """

    DB_USER = app.config.get('DB_USER', 'postgres')
    DB_PASSWORD = app.config.get('DB_PASSWORD', 'dbpass')
    DB_NAME = app.config.get('DB_NAME', 'envirolens')

    DB.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    DB.disconnect()

    return Response('DB is successfully connected!')
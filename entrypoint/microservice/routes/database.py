# Database routes
# Routes related with interaction with the database

import os
from flask import (
    Blueprint, flash, g, request, jsonify, current_app as app, render_template, url_for,
    Response
)
from werkzeug.exceptions import abort
from ..config import config_db


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
def get_documents():
    """
    At this endpoint you get the documents that you provided in the JSON body.

    JSON structure:
    {
        "document_ids" : [list of document ids]
    }

    The function returns a JSON response with the data of the documents. It is limited to
    output maximum of 10 documents.
    """

    # connect to the database:
    db = config_db.get_db()
    if db.cursor is None:
        return jsonify({'Error' : 'The connection could not be established'})

    document_ids = request.json.get('document_ids', None)

    # If the "document_ids" parameter was not set:
    if document_ids is None:
        return jsonify(
            {'Message' : 'You need to provide json with "document_ids" : [list of documents ids] value'}
        )

    statement = "SELECT * FROM documents WHERE document_id IN %s;"
    db.cursor.execute(statement, (tuple(document_ids), ))

    # Enumerating the fields
    num_fields = len(db.cursor.description)
    field_names = [i[0] for i in db.cursor.description]
    documents = [{ field_names[i]: row[i] for i in range(num_fields) } for row in db.cursor.fetchall()]

    # Cleaning the output:
    # - removing fulltext field
    # - slicing down the fulltext_cleaned field to 500 chars
    # - we return only the first 10 results
    for i in range(len(documents)):
        if documents[i]['fulltext_cleaned'] is not None:
            documents[i]['fulltext_cleaned'] = documents[i]['fulltext_cleaned'][:500]
        documents[i].pop('fulltext')
    config_db.close_db()
    return jsonify(documents[:10])

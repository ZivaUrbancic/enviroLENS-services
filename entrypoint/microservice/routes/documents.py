# Routes related to document retrieval microservice

import sys
import requests
from flask import (
    Blueprint, flash, g, redirect, request, session, url_for, jsonify, current_app as app
)
from ..config import config_db
from werkzeug.exceptions import abort

bp = Blueprint('documents', __name__, url_prefix='/api/v1/documents')

@bp.route('/', methods=['GET'])
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

    document_ids = request.args.get('document_ids', None)

    # If the "document_ids" parameter was not set:
    if document_ids is None:
        return jsonify(
            {'Message' : 'You need to provide query param "document_ids" : [comma separated set of documents ids]'}
        )

    statement = "SELECT * FROM documents WHERE document_id IN %s;"
    db.cursor.execute(statement, (tuple(document_ids.split(',')), ))

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

@bp.route('/<doc_id>', methods=['GET'])
def retrieve_document(doc_id):
    """
    At this endpoint you will retrieve a single document, if it exist. GET method on route 
    documents/<document_id> will return you the JSON of the document of the specified id.
    """

    db = config_db.get_db()
    if db.cursor is None:
        return jsonify({'Error' : 'The connection could not be established'}), 400
    
    try:
        statement = "SELECT * FROM documents WHERE document_id= %s;"
        db.cursor.execute(statement, tuple([doc_id]))
    except:
        return jsonify({'Error' : 'You provided invalid document id.'}), 400

    # Enumerating the fields
    num_fields = len(db.cursor.description)
    field_names = [i[0] for i in db.cursor.description]
    documents = [{ field_names[i]: row[i] for i in range(num_fields) } for row in db.cursor.fetchall()]

    # If we found no results:
    if len(documents) == 0:
        return jsonify({'Error' : 'Document with given id does not exist'}), 400

    # Cleaning the output:
    # - removing fulltext field
    # - slicing down the fulltext_cleaned field to 500 chars
    # - we return only the first 10 results
    for i in range(len(documents)):
        if documents[i]['fulltext_cleaned'] is not None:
            documents[i]['fulltext_cleaned'] = documents[i]['fulltext_cleaned'][:500]
        documents[i].pop('fulltext')
    config_db.close_db()
    return jsonify(documents[:1])

@bp.route('/retrieve', methods=['GET'])
def retrieve():
    """
    Do GET request to this endpoint and provide additional query parameters
        query : (your query), default = ""
        m : (number of results), default=5

    In response you will receive json of the following format:

    "documents_metadata": [
    {
      "celex_num": "52008DC0645",
      "date": "17/10/2008",
      "document_source": "eurlex",
      "fulltextlink": null,
      "title": "Communication from ..."
      },
      ]

    Example request
    {BASE_URL}/api/v1/documents/retrieve?query=deforestation&m=10
    will return top 10 documents matching your query.
    """

    text = request.args.get('query')
    HOST = app.config.get('RETRIEVAL_HOST')
    PORT = app.config.get('RETRIEVAL_PORT')
    query_params = {
        'query' : request.args.get('query', "")
    }
    r = requests.get(f"http://{HOST}:{PORT}/api/v1/docRetrieval/retrieval", params=query_params)
    return jsonify(r.json())



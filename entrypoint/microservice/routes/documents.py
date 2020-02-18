# All routes related to /documents endpoint
# We will provide the following routes:
#   /documents
#   /documents/id
#   /documents/id/similar
#   /documents/id/similarity_update
#   /documents/retrieve

import sys
import requests
from flask import (
    Blueprint, flash, g, redirect, request, session, url_for, jsonify, current_app as app
)
from ..config import config_db
from werkzeug.exceptions import abort

bp = Blueprint('documents', __name__, url_prefix='/api/v1/documents')

def get_documents_from_db(document_ids):
    """
    Function receives a list of document ids and returns a list of dictionaries of documents data.

    Parameters:
        documents_ids : list(int)
            list of document ids
    
    Returns:
        success (boolean), list of dictionaries of document data if the extraction from the database was successful.
    """

    db = config_db.get_db()
    if db.cursor is None:
        return False, {'Error' : 'The connection could not be established'}
    
    statement = "SELECT * FROM documents WHERE document_id IN %s;"
    try:
        db.cursor.execute(statement, (tuple(document_ids),))
    except:
        return False, {'Error' : 'You provided invalid document ids.'}
    
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

    return True, documents[:10]


@bp.route('/', methods=['GET'])
def get_documents():
    """
    At this endpoint you get the documents that you provided in the query parameters.

    query parameters:
        * document_ids : Space separated set of document ids

    The function returns a JSON response with the data of the documents. It is limited to
    output maximum of 10 documents.
    """

    document_ids = request.args.get('document_ids', None)

    # If the "document_ids" parameter was not set:
    if document_ids is None:
        return jsonify(
            {'Message' : 'You need to provide query param "document_ids" : [comma separated set of documents ids]'}
        )

    success, output = get_documents_from_db(document_ids.split(','))
    if success:
        return jsonify(output), 200
    else:
        return jsonify(output), 400

@bp.route('/<doc_id>', methods=['GET'])
def retrieve_document(doc_id):
    """
    At this endpoint you will retrieve a single document, if it exist. GET method on route 
    documents/<document_id> will return you the JSON of the document of the specified id.
    """

    success, output = get_documents_from_db([doc_id])
    if success:
        return jsonify(output), 200
    else:
        return jsonify(output), 400

@bp.route('/<doc_id>/similar', methods=['GET'])
def get_similar_documents(doc_id):
    """
    At this endpoint you will be able to get documents similar to document `doc_id`.
    You can provide additional query_parameter:
        * get_k int (number of results), default = 5
    
    In response you will receive json of the following format:

    {
    "finish": true,
    "similar_documents": [
        1000017599,
        1000017600,
        1000017598,
        1000017597,
        1000017596,
        1000017593,
        1000017595,
        1000017594
    ],
    "similarities": [
        [
            1000017599,
            0.199445346504904
        ],
        [
            1000017600,
            0.19275458304224
        ],
        [
            1000017598,
            0.191803893650522
        ],
        [
            1000017597,
            0.190294593704065
        ],
        [
            1000017596,
            0.190035190653879
        ],
        [
            1000017593,
            0.189315287176367
        ],
        [
            1000017595,
            0.189190944259772
        ],
        [
            1000017594,
            0.184603884562228
        ]
    ]
    }

    Example request
    {BASE_URL}/api/v1/documents/123?get_k=5
    will return top 5 similar documents to document with id 123.
    """

    HOST = app.config.get('SIMILARITY_HOST')
    PORT = app.config.get('SIMILARITY_PORT')
    
    query_params = {
        'document_id' : doc_id,
        'get_k' : request.args.get('get_k', 5)
    }
    
    r = requests.get(f"http://{HOST}:{PORT}/api/v1/similarity/get_similarities", params=query_params)
    return jsonify(r.json())

@bp.route('/<doc_id>/similarity_update', methods=['POST'])
def update_document_similarities(doc_id):
    """
    Make a request with GET method to this endpoint.

    Example request:
    {BASE_URL}/api/v1/documents/id/similarity_update
    """

    HOST = app.config.get('SIMILARITY_HOST')
    PORT = app.config.get('SIMILARITY_PORT')
    query_params = {
        'document_id': doc_id,
    }
    r = requests.get(f"http://{HOST}:{PORT}/api/v1/similarity/new_document_embedding", params=query_params)
    return jsonify(r.json())

@bp.route('/find', methods=['GET'])
def find_documents():
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



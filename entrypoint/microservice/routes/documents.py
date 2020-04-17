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
from werkzeug.exceptions import abort
from ..config import config_db

bp = Blueprint('documents', __name__, url_prefix='/api/v1/documents')

@bp.route('/', methods=['GET'])
def get_documents():
    """
    At this endpoint you get the documents that you provided in the query parameters.

    query parameters:
        * document_ids : Space separated set of document ids

    The function returns a JSON response with the data of the documents. It is limited to
    output maximum of 100 documents.

    If query was successful, you will receive JSON list of dictionaries, each containing metadata of specific document.
    Otherwise you will receive JSON dictionary with an `error` attribute, showing the error.
    """

    document_ids = request.args.get('document_ids', None)

    # If the "document_ids" parameter was not set:
    if document_ids is None:
        return jsonify(
            {'Message' : 'You need to provide query param "document_ids" : [comma separated set of documents ids]'}
        )

    db = config_db.get_db()
    # We allows a maximum of 100 documents per query.
    success, output = db.get_documents_from_db(document_ids.split(',')[:100])
    if success:
        return jsonify({
            "documents" : output
        }), 200
    else:
        # Output is already a dictionary with an error message.
        return jsonify(output), 400

@bp.route('/<doc_id>', methods=['GET'])
def retrieve_document(doc_id):
    """
    At this endpoint you will retrieve a single document, if it exist. GET method on route
    documents/<document_id> will return you the JSON of the document of the specified id.

    If query was successful, you will receive JSON list containing a single dictionary of document metadata.
    Otherwise you will receive JSON dictionary with an `error` attribute, showing the error.
    """

    db = config_db.get_db()
    success, output = db.get_documents_from_db([doc_id])
    if success:
        return jsonify({
            "documents" : output
        }), 200
    else:
        return jsonify(output), 400

@bp.route('/<doc_id>/similar', methods=['GET'])
def get_similar_documents(doc_id):
    """
    At this endpoint you will be able to get documents similar to document `doc_id`.
    You can provide additional query_parameter:
        * get_k int (number of results), default = 5

    In response you will receive json of the following format:

    [
        {
            ... document metadata ...
            similarity : x.abcdefgh
        },
        {
            ... document metadata ...
            similarity : x.abcdefgh
        },
    ]

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
    json_response = r.json()
    if 'similar_documents' in json_response:
        # If request was successful, we get the documents from the db and and similarities to them.
        documents_ids = json_response.get('similar_documents', [])
        similarities = json_response.get('similarities', [])
        similarities_dictionary = {doc_id : sim for doc_id, sim in similarities}

        db = config_db.get_db()
        success, output = db.get_documents_from_db(documents_ids)
        if success:
            for doc in output:
                document_id = doc['document_id']
                doc['similarity'] = similarities_dictionary[document_id]
            return jsonify({
                "documents" : output
                }), 200
        else:
            return jsonify(output), 400
    else:
        return jsonify(json_response), 400

@bp.route('/<doc_id>/similarity_update', methods=['POST'])
def update_document_similarities(doc_id):
    """
    Make a request with POST method to this endpoint.

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

@bp.route('/search', methods=['GET'])
def search_documents():
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

    HOST = app.config.get('RETRIEVAL_HOST')
    PORT = app.config.get('RETRIEVAL_PORT')

    query_params = {
        'text': request.args.get('text', default=None),
        'sources': request.args.get('sources', default=None),
        'locations': request.args.get('locations', default=None),
        'languages': request.args.get('languages', default=None),
        'informea': request.args.get('informea', default=None),
        'limit': request.args.get('limit', default=None),
        'page': request.args.get('page', default=None)
    }
    r = requests.get(f"http://{HOST}:{PORT}/api/v1/search", params=query_params)
    return jsonify(r.json())
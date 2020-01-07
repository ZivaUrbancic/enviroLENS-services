# Routes related to document similarity microservice

import sys

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for, jsonify, current_app as app
)
from werkzeug.exceptions import abort

import requests


#################################################
# Initialize the models
#################################################

# TODO: include the model initialization function

#################################################
# Setup the embeddings blueprint
#################################################

# TODO: provide an appropriate route name and prefix
bp = Blueprint('similarity', __name__, url_prefix='/api/v1/similarity')


@bp.route('/', methods=['GET'])
def index():
    # TODO: provide an appropriate output
    return abort(501)

@bp.route('/get_similar', methods=['GET'])
def get_embedding():
    """
    Do GET request to this endpoint and provide additional query parameters
        document_id : (your query), default = None
        get_k : (number of results), default = 5

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
    {BASE_URL}/api/v1/similarity/get_similar?document_id=1000017605&get_k=5 
    will return top 5 similar documents to document with id 1000017605.
    """

    HOST = app.config.get('SIMILARITY_HOST')
    PORT = app.config.get('SIMILARITY_PORT')

    print(f"Making request to: http://{HOST}:{PORT}/api/v1/similarity/get_similarities")

    query_params = {
        'document_id' : request.args.get('document_id', "1"),
        'get_k' : request.args.get('get_k', 5)
    }

    r = requests.get(f"http://{HOST}:{PORT}/api/v1/similarity/get_similarities", params=query_params)

    return jsonify(r.json())

@bp.route('/update_similarities', methods=['GET'])
def update_similarities():
    """
    Make a request with GET method to this endpoint. Add additional query parameters:

        document_id : {id of the document}

    Example request:
    {BASE_URL}/api/v1/similarity/update_similarities?document_id=1000017605 
    """

    document_id = request.args.get('document_id', default=None, type=int)

    HOST = app.config.get('SIMILARITY_HOST')
    PORT = app.config.get('SIMILARITY_PORT')

    print(f"Making request to: http://{HOST}:{PORT}/api/v1/similarity/new_document_embedding")

    query_params = {
        'document_id' :request.args.get('document_id', default=None, type=int),
    }

    r = requests.get(f"http://{HOST}:{PORT}/api/v1/similarity/new_document_embedding", params=query_params)
    
    return jsonify(r.json())
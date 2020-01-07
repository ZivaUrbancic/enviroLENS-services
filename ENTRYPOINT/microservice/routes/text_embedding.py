# Routes related to english text embedding model

import sys

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for, jsonify, current_app as app
)
from werkzeug.exceptions import abort

import requests

bp = Blueprint('embedding', __name__, url_prefix='/api/v1/embedding')


@bp.route('/', methods=['GET'])
def index():
    # TODO: provide an appropriate output
    return abort(501)

@bp.route('/create', methods=['GET'])
def get_embedding():
    """
    Do GET request to this endpoint and provide additional query parameters
        text : (text you wish to get the embedding for), default = ""
        language : (language of the text), default = None

    In response you will receive json with the embedding of the text:

    {
    "embedding": [
        // LINES SKIPPED //
    ],
    "language_model": "en",
    "text": "ice cream",
    "tokens": [
        {
        "count": 1,
        "token": "ice"
        },
        {
        "count": 1,
        "token": "cream"
        }
    ]
    }

    Example request
    {BASE_URL}/api/v1/embedding/create?text=ice cream&language=en 
    will return the embedding of the word ice cream.
    """
    
    HOST = app.config.get('EMBEDDING_HOST')
    PORT = app.config.get('EMBEDDING_PORT')

    print(f"Making request to: http://{HOST}:{PORT}/api/v1/embeddings/create")

    query_params = {
        'text' : request.args.get('text', ""),
        "language" : request.args.get('language', None)
    }

    r = requests.get(f"http://{HOST}:{PORT}/api/v1/embeddings/create", params=query_params)

    return jsonify(r.json())

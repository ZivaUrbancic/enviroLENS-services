# Routes related to document retrieval microservice

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
bp = Blueprint('retrieval', __name__, url_prefix='/api/v1/retrieval')


@bp.route('/', methods=['GET'])
def index():
    # TODO: provide an appropriate output
    return abort(501)

@bp.route('/retrieve', methods=['GET'])
def get_embedding():
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
    {BASE_URL}/api/v1/retrieval/retrieve?query=deforestation&m=10 
    will return top 10 documents matching your query.
    """
    
    text = request.json.get('query')

    HOST = app.config.get('RETRIEVAL_HOST')
    PORT = app.config.get('RETRIEVAL_PORT')

    print(f"Making request to: http://{HOST}:{PORT}/api/v1/docRetrieval/retrieval")

    query_params = {
        'query' : request.args.get('query', "")
    }

    r = requests.get(f"http://{HOST}:{PORT}/api/v1/docRetrieval/retrieval", params=query_params)

    return jsonify(r.json())

# TODO: add an appropriate route name
@bp.route('/second', methods=['GET', 'POST'])
def second():
    # TODO: assign the appropriate variables
    variable = None
    if request.method == 'GET':
        # retrieve the correct query parameters
        variable = request.args.get('variable', default='', type=str)
    elif request.method == 'POST':
        # retrieve the text posted to the route
        variable = request.json['variable']
    else:
        # TODO: log exception
        return abort(405)

    try:
        # TODO: add the main functionality with the model and variable
        finish = True
    except Exception as e:
        # TODO: log exception
        # something went wrong with the request
        return abort(400, str(e))
    else:
        # TODO: return the response
        return jsonify({
            "finish": finish
        })
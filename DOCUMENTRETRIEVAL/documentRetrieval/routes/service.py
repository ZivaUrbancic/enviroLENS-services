# Embedding Route
# Routes related to creatiung text embeddings

import sys
import requests
import json


from flask import (
    Blueprint, flash, g, redirect, request, session, url_for, jsonify, current_app as app
)
from werkzeug.exceptions import abort


#################################################
# Initialize the models
#################################################
# get the database configuration object
from ..config import config_db



from ..library.documentRetrieval import tfidf_score_str
from ..library.documentRetrieval import change_dict_structure
from ..library.postgresql import PostgresQL





## initialize text embedding model
model = PostgresQL()

#################################################
# Setup the embeddings blueprint
#################################################


bp = Blueprint('docRetrieval', __name__, url_prefix='/api/v1/docRetrieval')


@bp.route('/', methods=['GET'])
def index():
    # TODO: provide an appropriate output
    return abort(501)

@bp.route('/retrieval', methods=['GET', 'POST'])
def retrieval():

    query = None
    m = None
    if request.method == 'GET':
        query=request.args.get('query', default='', type=str)
        m= request.args.get('m', default=5, type=int)

    elif request.method == 'POST':
        query=request.json['query']
        m = request.json['m']

    else:
        # TODO: log exception
        return abort(405)

    if query == '':
        raise Exception('Missing input: query') 
    if "'" in query or "\"" in query:
        raise Exception('Wrong query: do not use quotation marks') 

    HOST = app.config.get('TEXT_EMBEDDING_HOST', 'localhost')
    PORT = app.config.get('TEXT_EMBEDDING_PORT', '4000')

    query_params = {'query': query}
    


    r = requests.get(f"http://{HOST}:{PORT}/api/v1/embeddings/expand", params=query_params)
    r = json.loads(r.text)
    tokens = r.get("expanded_query")
    


    try:
        db = config_db.get_db()
        docs = db.db_query(tokens)
        number_all_documents = db.db_nb_docs()
        texts = change_dict_structure(docs) 
        tfidf_score = tfidf_score_str(tokens, texts, 'tfidf_sum', number_all_documents, m) 
        metadata = db.db_return_docs_metadata(tfidf_score)

    except Exception as e:
        # TODO: log exception
        # something went wrong with the request
        return abort(400, str(e))
    else:
        # TODO: return the response
        return jsonify({
            "documents_metadata": metadata
        })


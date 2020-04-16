# Embedding Route
# Routes related to creatiung text embeddings

import sys
import json
import requests
import math
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for, jsonify, current_app as app
)
from werkzeug.exceptions import abort

#################################################
# Static values
#################################################

BASE_URL = "http://envirolens.ijs.si/api/v1/search"

#################################################
# Initialize the elasticsearch component
#################################################

# get the database configuration object
from ..config import config_es

# add helper functions
def format_document(document):
    return {
        "document_id": document["document_id"],
        "title": document["title"],
        "abstract": document["abstract"],
        "link": document["link"],
        "date": document["date"],
        "celex": document["celex"],
        "keywords": document["keywords"],
        "source": document["source"],
        "informea": document["informea"],
        "keywords": document["keywords"],
        "languages": [lang.lower() for lang in document["languages"]] if document["languages"] else []
    }


def format_url(url, params):
    # part the url
    url_parts = list(urlparse(url))
    # get the query parameters of the url
    query = dict(parse_qsl(url_parts[4]))
    # add the query parameters
    query.update(params)
    # encode the query parameters
    url_parts[4] = urlencode(query)
    # create the url
    return urlunparse(url_parts)

#################################################
# Setup the embeddings blueprint
#################################################

bp = Blueprint('search', __name__, url_prefix='/api/v1/search')


@bp.route('/', methods=['GET'])
def retrieval():
    try:
        text = None
        limit = None
        page = None
        if request.method == 'GET':
            text = request.args.get('text', default='', type=str)
            limit = request.args.get('limit', default=20, type=int)
            page = request.args.get('page', default=1, type=int)
        else:
            # TODO: log exception
            return abort(405)

        if text == '':
            raise Exception('Missing input: text')
        if "'" in text or "\"" in text:
            raise Exception('Wrong query: do not use quotation marks')

        #HOST = app.config.get('TEXT_EMBEDDING_HOST', 'localhost')
        #PORT = app.config.get('TEXT_EMBEDDING_PORT', '4222')

        query_params = {
            'query': text
        }

        #r = requests.get(f"http://{HOST}:{PORT}/api/v1/embeddings/expand", params=query_params)
        #r = json.loads(r.text)
        #tokens = r.get("expanded_query", [])

        # establish connection with elasticsearch
        es = config_es.get_es()

        # TODO: create the elasticsearch query object

        offset = (page - 1) * limit
        size = limit

        es_query = {
            "from": offset,
            "size": size,
            "query": {
                "bool": {
                    "should": [{
                        "match": { "title": text }
                    }, {
                        "match": { "fulltext": text }
                    }, {
                        "match": { "abstract": text }
                    }]
                }
            }
        }

        # run the query on elasticsearch
        results = es.search(index="envirolens", body=es_query)

        # prepare output of the elasticsearch response
        documents = [format_document(document["_source"]) for document in results["hits"]["hits"]]

        # prepare metadata information for easier navigation
        TOTAL_HITS = results["hits"]["total"]["value"]
        TOTAL_PAGES = math.ceil(TOTAL_HITS / size)

        prev_page = format_url(BASE_URL, {
            "text": text,
            "limit": limit,
            "page": page - 1
        }) if page - 1 > 0 else None

        next_page = format_url(BASE_URL, {
            "text": text,
            "limit": limit,
            "page": page + 1
        }) if page + 1 <= TOTAL_PAGES else None



    except Exception as e:
        # TODO: log exception
        # something went wrong with the request
        return abort(400, str(e))
    else:
        # TODO: return the documents
        return jsonify({
            "query": {
                "text": text,
                "limit": limit,
                "page": page
            },
            "documents": documents,
            "metadata": {
                "total_hits": TOTAL_HITS,
                "total_pages": TOTAL_PAGES,
                "prev_page": prev_page,
                "next_page": next_page
            }
        })

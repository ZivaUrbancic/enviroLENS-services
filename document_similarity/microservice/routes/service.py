# Document comparison Route
# Routes related to comparing documents among eachother

from flask import (
    Blueprint, request, jsonify, current_app as app
)
from werkzeug.exceptions import abort
import requests
# from psycopg2.sql import SQL, Identifier

#################################################
# Initialize the models
#################################################

from ..library.document_similarity import DocumentSimilarity
# from ..library.postgresql import PostgresQL
from ..config import config_db

#################################################
# Get parameters from .config file
#################################################

# url to text embedding service
text_embedding_url = app.config['TEXT_EMBEDDING_URL']


#################################################
# Setup the similarity blueprint
#################################################

bp = Blueprint('similarity', __name__, url_prefix='/api/v1/similarity')


#################################################
# Index route:
#################################################

@bp.route('/', methods=['GET'])
def index():
    # TODO: provide an appropriate output
    return abort(501)


#################################################
# Route for updating the database
#################################################

@bp.route('/new_document_embedding', methods=['GET', 'POST'])
def update_similarities():
    # TODO: write documentation


    # connect to the database:
    pg = config_db.get_db()


    # get document id (and optionally language) as the parameter
    if request.method == 'GET':
        try:
            document_id = request.args.get('document_id', default=None, type=int)
            language = request.args.get('language', default='en', type=str)
        except Exception as e:
            return abort(401, "Could not retrieve parameter 'document_id', method = 'GET'. " + str(e))
    elif request.method == 'POST':
        try:
            document_id = request.json['document_id']
            language = request.json['language']
        except Exception as e:
            return abort(401, "Could not retrieve parameter 'document_id', method = 'POST'. " + str(e))
    else:
        return abort(405)


    # Retrieve the embeddings from the database

    try:
        # Retrieve IDs and embeddings of documents in the database
        indices, embeddings = pg.retrieve_embeddings()
    except Exception as e:
        return abort(404, "Could not retrieve document embeddings from the database. " + str(e))


    # Retrieve the document's text from the database

    try:
        # Retrieve a vocabulary containing the full text, the abstract and the title of the document from the database.
        retrieved = pg.retrieve_textual_data(document_id)

        # Take the first that is not empty or None (priorities: full text > abstract > title).
        document_text = retrieved['fulltext_cleaned']
        if document_text == "" or document_text is None:
            document_text = retrieved['abstract']
        if document_text == "" or document_text is None:
            document_text = retrieved['title']

        # If none of those are useful, raise an exception
        if document_text == "" or document_text is None:
            raise Exception("Could not retrieve any text for the document with ID {}.".format(document_id))
    except Exception as e:
        return abort(400, "Could not retrieve text of the document from the database. "+str(e))


    # Construct the new document's embedding

    try:
        # Call the text-embedding-service and produce the embedding
        params = {'text': document_text, 'language': language}
        service_response = (requests.post(url=text_embedding_url, json=params)).json()
        if 'embedding' in service_response:
            new_embedding = service_response['embedding']
        elif 'error' in service_response:
            raise Exception(str(service_response['error']))
        else:
            raise Exception("Something went terribly wrong.")
    except Exception as e:
        return abort(400, "Could not retrieve the embedding from the text embedding service. " + str(e))


    # Compute similarities with other documents

    try:
        # initialize the model
        similarity = DocumentSimilarity(embedding=embeddings, indices=indices)
        # retrieve the new similarities to be added to the table
        additional_similarities = similarity.new_document(document_id, new_embedding)
    except Exception as e:
        return abort(400, "Could not retrieve similarities between documents. " + str(e))


    # Insert the new embedding into the database

    try:
        # Insert the new embedding (indexed by document_id) into 'document_embeddings' table
        pg.insert_new_embedding(document_id, new_embedding)
    except Exception as e:
        return abort(400, "Could not add the new embedding into the table 'document_embeddings'. " + str(e))


    # Insert similarities into the database

    try:
        for i, j, sim in additional_similarities:
            # Insert the similarity score 'sim' between document with id 'i' and document with id 'j' into
            # 'similarities' table
            pg.insert_new_similarity(i, j, sim)
    except Exception as e:
        return abort(400, "Could not add the additional similarities into the table 'similarities'. " + str(e))


    # Return the result
    return jsonify({
        "embedding": new_embedding,
        "additional similarities": additional_similarities,
        "indices": indices
    })


#################################################
# Route for retrieving similar documents:
#################################################

@bp.route('/get_similarities', methods=['GET', 'POST'])
def get_similarities():
    # TODO: write documentation

    # Retrieve query parameters 'document_id' and 'get_k'
    if request.method == 'GET':
        doc_id = request.args.get('document_id', default=None, type=int)
        k = request.args.get('get_k', default=5, type=int)
    elif request.method == 'POST':
        doc_id = request.json['document_id']
        k = request.json['get_k']
    else:
        # TODO: log exception
        return abort(405)

    try:
        # retrieve the similarity matrix
        # connect to the database:
        try:
            pg = config_db.get_db()
        except Exception as e:
            return abort(400, str(e) + ' Accessing the database')
        # TODO: change the expression if needed

        # Retrieve k most similar documents of the source document from the database
        result_indices, result = pg.retrieve_similarities(doc_id, k)
    except Exception as e:
        # TODO: log exception
        # something went wrong with the request
        return abort(400, str(e)+' This error occured in service.py')
    else:
        return jsonify({
            "similar_documents": result_indices,
            "similarities": result
        })

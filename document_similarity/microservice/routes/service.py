# Document comparison Route
# Routes related to comparing documents among eachother

from flask import (
    Blueprint, request, jsonify, current_app as app
)
from werkzeug.exceptions import abort
import requests

#################################################
# Initialize the models
#################################################

from ..library.document_similarity import DocumentSimilarity
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
    # connect to the database:
    pg = config_db.get_db()

    # get document id (and optionally language) as the parameter
    if request.method == 'GET':
        try:
            document_id = request.args.get('document_id', default=None, type=int)
            language = request.args.get('language', default='en', type=str)
        except Exception as e:
            return abort(401, "Could not retrieve parameter 'document_id'. " + str(e))
    elif request.method == 'POST':
        try:
            document_id = request.json['document_id']
            language = request.json['language']
        except Exception as e:
            return abort(401, "Could not retrieve parameter 'document_id'. " + str(e))
    else:
        return abort(405)

    # Retrieve the embeddings from the database
    try:
        # Retrieve IDs and embeddings of documents in the database
        indices, embeddings = pg.retrieve_embeddings()
    except Exception as e:
        return abort(502, "Could not retrieve document embeddings from the database. " + str(e))

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
        return abort(502, "Something went wrong when retrieving the text of the document from the database. "+str(e))

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
            raise Exception("Something went wrong when constructing the embedding.")
    except Exception as e:
        return abort(502, "Could not retrieve the embedding from the text embedding service. " + str(e))

    # Compute similarities with other documents
    try:
        # initialize the model
        similarity = DocumentSimilarity(embedding=embeddings, indices=indices)
        # retrieve the new similarities to be added to the table
        additional_similarities = similarity.new_document(document_id, new_embedding)
    except Exception as e:
        return abort(502, "Could not retrieve similarities between documents. " + str(e))

    # Insert the new embedding into the database
    try:
        # Insert the new embedding (indexed by document_id) into 'document_embeddings' table
        pg.insert_new_embedding(document_id, new_embedding)
    except Exception as e:
        return abort(502, "Could not add the new embedding into the table 'document_embeddings'. " + str(e))

    # Insert similarities into the database
    try:
        for i, j, sim in additional_similarities:
            # Insert the similarity score 'sim' between document with id 'i' and document with id 'j' into
            # 'similarities' table
            pg.insert_new_similarity(i, j, sim)
    except Exception as e:
        return abort(502, "Could not add the additional similarities into the table 'similarities'. " + str(e))

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
    # Retrieve query parameters
    try:

        # Retrieving parameters for method GET:
        if request.method == 'GET':
            doc_id = request.args.get('document_id', default=None, type=int)
            k = request.args.get('limit', default=5, type=int)
            page = request.args.get('page', default=None, type=int)
            offset = request.args.get('offset', default=None, type=int)

        # Retrieving parameters for method POST:
        elif request.method == 'POST':
            doc_id = request.json['document_id']
            k = request.json['limit']
            page = request.json['page']
            offset = request.json['offset']
        else:
            return abort(405)

        # Initialize missing parameters and check if they all fit together
        if offset is None and page is None:
            offset = 0
        elif offset is None:
            offset = page * k
        elif offset != page * k and page is not None:
            raise Exception("The parameter 'offset' must be the product of parameters 'limit' and 'page'.")
    except Exception as e:
        return abort(401, "Could not retrieve the parameters. " + str(e))

    # Retrieve the information about most similar documents
    try:
        # connect to the database:
        try:
            pg = config_db.get_db()
        except Exception as e:
            return abort(400, 'Error accessing the database. ' + str(e))

        # Retrieve k most similar documents of the source document from the database
        result_indices, result = pg.retrieve_similarities(doc_id, k, offset)
    except Exception as e:
        # something went wrong with the request
        return abort(400, 'Could not retrieve from table similarities. ' + str(e))
    else:
        # Return the result
        params = {
            "document_id": doc_id,
            "page": page,
            "limit": k,
            "offset": offset
        }
        return jsonify({
            "query_parameters": params,
            "similar_documents": result_indices,
            "similarities": result
        })

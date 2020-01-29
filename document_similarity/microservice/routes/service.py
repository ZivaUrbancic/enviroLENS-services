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


    # get document id as the parameter
    if request.method == 'GET':
        try:
            document_id = request.args.get('document_id', default=None, type=int)
        except Exception as e:
            return abort(401, "Could not retrieve parameter 'document_id', method = 'GET'. " + str(e))
    elif request.method == 'POST':
        try:
            document_id = request.json['document_id']
        except Exception as e:
            return abort(401, "Could not retrieve parameter 'document_id', method = 'POST'. " + str(e))
    else:
        return abort(405)


    # Retrieve the embeddings from the database

    try:
        # get embeddings from postgres
        loaded_embedding = pg.retrieve('document_embeddings')

        # Separate the result into a list of indices and a matrix of embeddings
        indices = [embedding['document_id'] for embedding in loaded_embedding]
        embeddings = [embedding['vector'] for embedding in loaded_embedding]
    except Exception as e:
        return abort(404, "Could not retrieve document embeddings from the database. " + str(e))


    # Retrieve the document's text from the database

    try:
        # Retrieve the full text, the abstract and the title of the document.
        retrieved = pg.retrieve('documents',
                                names_of_columns='fulltext_cleaned, abstract, title',
                                constraints="""WHERE document_id={}""".format(document_id))

        # Take the first that is not empty or None (priorities: full text > abstract > title).
        document_text = retrieved[0]['fulltext_cleaned']
        if document_text == "" or document_text is None:
            document_text = retrieved[0]['abstract']
        if document_text == "" or document_text is None:
            document_text = retrieved[0]['title']

        # If none of those are useful, raise an exception
        if document_text == "" or document_text is None:
            raise Exception("Could not retrieve any text for this document.")
    except Exception as e:
        return abort(400, "Could not retrieve text of the document from the database. "+str(e))


    # Construct the new document's embedding

    # TODO: add language_model parameter
    try:
        # Call the text-embedding-service and produce the embedding
        params = {'text': document_text, 'language': 'EN'}
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
        values = """VALUES ({}, ARRAY{})""".format(document_id, new_embedding)
        pg.insert('document_embeddings', values)
    except Exception as e:
        return abort(400, "Could not add the new embedding into the table 'document_embeddings'. " + str(e))


    # Insert similarities into the database

    try:
        for i, j, sim in additional_similarities:
            # Insert the similarity score 'sim' between document with id 'i' and document with id 'j' into
            # 'similarities' table
            values = """VALUES ({}, {}, {})""".format(i, j, sim)
            pg.insert('similarities', values)
    except Exception as e:
        return abort(400, "Could not add the additional similarities into the table 'similarities'. " + str(e))


    # Return the result

    finish = True
    return jsonify({
            "embedding": new_embedding,
            "additional similarities": additional_similarities,
            "indices": indices,
            "finish": finish
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
        pg = config_db.get_db()
        # TODO: change the expression if needed
        # get only the lines in table 'similarities' where the first document has id doc_id
        # sort them by the similarity column, descending

        # SQL constraints:
        constraints = """WHERE document1_id = {}
            ORDER BY similarity_score DESC""".format(doc_id)

        # Retrieving from postgres using constraints
        similarity_list=pg.retrieve('similarities',
                                    names_of_columns='document2_id, similarity_score',
                                    constraints=constraints)

        # Taking only indices of k most similar documents
        result_indices = [entry['document2_id'] for entry in similarity_list[:k]]
        result = [(entry['document2_id'], entry['similarity_score']) for entry in similarity_list[:k]]
        finish = True
        pg.disconnect()
    except Exception as e:
        # TODO: log exception
        # something went wrong with the request
        return abort(400, str(e))
    else:
        return jsonify({
            "similar_documents": result_indices,
            "similarities": result,
            "finish": finish
        })

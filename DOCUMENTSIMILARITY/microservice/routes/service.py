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
from ..library.postgresql import PostgresQL

#################################################
# Get parameters from .config file
#################################################

# database parameters
database_name = app.config['DATABASE_NAME']
database_user = app.config['DATABASE_USER']
database_password = app.config['DATABASE_PASSWORD']
# url to text embedding service
text_embedding_url = app.config['TEXT_EMBEDDING_URL']


#################################################
# Connect to the database
#################################################

pg = PostgresQL()
pg.connect(database=database_name, user=database_user,
                      password=database_password)


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


    # Retrieve 'document_id' as a request parameter

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
        loaded_embedding = pg.execute("""
            SELECT * FROM document_embeddings;
            """)
        # Separate the result into a list of indices and a matrix of embeddings
        indices = [embedding['document_id'] for embedding in loaded_embedding]
        embeddings = [embedding['vector'] for embedding in loaded_embedding]
    except Exception as e:
        return abort(404, "Could not retrieve document embeddings from the database. " + str(e))


    # Retrieve the document's text from the database

    try:
        statement = """
            SELECT fulltext_cleaned FROM documents
            WHERE document_id={};
            """.format(document_id)
        document_text = (pg.execute(statement))[0]['fulltext_cleaned']
        if document_text == "":
            statement = """
            SELECT abstract FROM documents
            WHERE document_id={};
            """.format(document_id)
            document_text = (pg.execute(statement))[0]['abstract']
            if document_text == "":
                statement = """
                SELECT title FROM documents
                WHERE document_id={};
                """.format(document_id)
                document_text = (pg.execute(statement))[0]['title']
    except Exception as e:
        return abort(400, "Could not retrieve text of the document from the database. "+str(e))


    # Construct the new document's embedding

    # TODO: add language_model parameter
    try:
        # Call the text-embedding-service and produce the embedding
        params = {'text': document_text, 'language': 'en'}
        service_response = requests.post(url=text_embedding_url, json=params).json()
        new_embedding = service_response['embedding']
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
        pg.execute("""
            INSERT INTO document_embeddings
            VALUES ({}, ARRAY{});
            """.format(document_id, new_embedding))
        pg.commit()
    except Exception as e:
        return abort(400, "Could not add the new embedding into the table 'document_embeddings'. " + str(e))


    # Insert similarities into the database

    try:
        for i, j, sim in additional_similarities:
            pg.execute("""
                INSERT INTO similarities
                VALUES ({}, {}, {});
                """.format(i, j, sim))
            pg.commit()
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
        k = request.args.get('get_k', default=None, type=int)
    elif request.method == 'POST':
        doc_id = request.json['document_id']
        k = request.json['get_k']
    else:
        # TODO: log exception
        return abort(405)

    try:
        # retrieve the similarity matrix
        pg = PostgresQL()
        pg.connect(database=database_name, user=database_user,
                   password=database_password)
        # TODO: change the expression if needed
        # get only the lines in table 'similarities' where the first document has id doc_id
        # sort them by the similarity column, descending
        similarity_list = pg.execute("""
            SELECT document2_id, similarity_score FROM similarities
            WHERE document1_id = {}
            ORDER BY similarity_score DESC;
            """.format(doc_id))
        result_indices = [entry['document2_id'] for entry in similarity_list[:k]]
        result = [(entry['document2_id'], entry['similarity_score']) for entry in similarity_list[:k]]
        finish = True
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

import psycopg2
from psycopg2.sql import Identifier, SQL

class PostgresQL:
    """Connection to the PostgresQL database

    Args:
        host (str): The host address. (Default "127.0.0.1")
        port (str): The port number. (Default "5432")

    """

    def __init__(self, host="127.0.0.1", port="5432"):
        self.host = host
        self.port = port
        #self.connection=False


    def connect(self, database, password, user="postgres"):
        """Connects to the database with the provided user and password

        Args:
            database (str): The database name.
            password (str): The password of the user.
            user (str): The postgresql user. (Default "postgres")
        """

        try:
            # create a connection
            self.connection = psycopg2.connect(
                user = user,
                password = password,
                host = self.host,
                port = self.port,
                database = database
            )
        except (Exception, psycopg2.Error) as error:
            # notify the user about the error
            self.connection = None

        try:
            # store the connection cursor
            self.cursor = self.connection.cursor()

        except (Exception, psycopg2.Error) as error:
            # notify the user about the error
            self.cursor = None


    def disconnect(self):
        """Disconnect the postgresql connection to the database"""
        if self.connection:
            self.cursor.close()
            self.connection.close()


    def execute(self, statement, params=None):
        """Execute the provided statement

        Args:
            statement (str): The postgresql statement to be executed.
            params (tuple): values to be formatted into the statement. (Default = None)

        Returns:
            list: a list of tuples containing the postgresql records.

        """
        if self.cursor is None:
            raise Exception("The connection is not established")
        else:
            if params is None:
                self.cursor.execute(statement)
            else:
                self.cursor.execute(statement, params)
            if self.cursor.description is not None:
                num_fields = len(self.cursor.description)
                field_names = [i[0] for i in self.cursor.description]
                return [{ field_names[i]: row[i] for i in range(num_fields) } for row in self.cursor.fetchall()]
            else:
                return None

    def retrieve_textual_data(self, doc_id):
        """Given an ID of a document, the method returns its full text, abstract and title from the database.

        Args:
            doc_id (int): the ID of the document in the database.

        Returns:
            vocabulary: a vocabulary with keys 'fulltext_cleaned', 'abstract' and 'title'.
        """

        statement = """
        SELECT fulltext_cleaned, abstract, title FROM documents
        WHERE document_id = %s;
        """
        return self.execute(statement,(doc_id,))[0]

    def retrieve_embeddings(self):
        """Retrieves all document embeddings currently in the database.

        Args:
            The method takes no arguments.

        Returns:
            tuple(list): Two lists: first with IDs of the documents with embeddings in the database and second with
                their embeddings.
        """

        statement = """
        SELECT * FROM document_embeddings;
        """
        loaded_embeddings = self.execute(statement)

        # Separate the result into a list of indices and a matrix of embeddings
        indices = [embedding['document_id'] for embedding in loaded_embeddings]
        embeddings = [embedding['vector'] for embedding in loaded_embeddings]
        return indices, embeddings

    def retrieve_similarities(self, doc_id, k=5, offset=0):
        """Given an ID of a document (and optionally parameters 'k' and 'offset') the method returns the IDs of 'k'
        documents that are most similar to the sample document, where we skip the first 'offset' most similar documents.
        For example, if k = 3 and offset = 10, the method will return the 11th, 12th and 13th most similar document.

        Args:
            doc_id (int): The ID of the sample document.
            k (int): The number of similar documents we want to find.
                (Default=5)
            offset (int): Number of top most similar documents that we want to skip.
                (Default=0)

        Returns:
            tuple(list): Two lists. The first contains the IDs of the retrieved documents. The second contains tuples
                of the IDs of the similar document and the similarity score between the retrieved document and the
                sample document.
        """

        statement="""
        SELECT document2_id, similarity_score FROM similarities
        WHERE document1_id = %s
        ORDER BY similarity_score DESC;
        """
        similarity_list = self.execute(statement, (doc_id,))
        result_indices = [entry['document2_id'] for entry in similarity_list[offset:(offset + k)]]
        result = [(entry['document2_id'], entry['similarity_score']) for entry in similarity_list[offset:(offset + k)]]
        return result_indices, result

    def insert(self, name_of_table, values, user_input):
        """Inserts values to a table.

        Args:
            name_of_table (string): Name of the table we want to insert into.
            values (string): SQL code describing values to insert. Example:
                '''VALUES ({}, {}, ARRAY {})'''
            user_input (list(miscellaneous)): values to be formatted into the statement.
        """

        statement =SQL("""
            INSERT INTO {table_name}
            """)
        values = SQL('').join([values, SQL(';')])
        statement = SQL(' ').join([statement, values])
        self.execute(statement.format(table_name=Identifier(name_of_table)), (*user_input,))
        self.commit()

    def insert_new_embedding(self, doc_id, embedding):
        """Inserts a new embedding into the database.

        Args:
            doc_id (int): The ID of the document whose embedding we're inserting.
            embedding (np.ndarray): The embedding we're inserting.

        Returns:
            The method doesn't return anything.
        """

        statement = """
            INSERT INTO document_embeddings
            VALUES (%s, %s);
            """
        self.execute(statement, (doc_id, embedding, ))
        self.commit()

    def insert_new_similarity(self, document1_id, document2_id, sim):
        """Inserts a new similarity into the database.

        Args:
            document1_id (int): The ID of the first of two documents.
            document2_id (int): The ID of the second of two documents.
            sim (np.single): Similarity score between given documents.

        Returns:
            The method doesn't return anything.
        """

        statement = """
            INSERT INTO similarities
            VALUES (%s, %s, %s);
            """
        self.execute(statement, (document1_id, document2_id, sim, ))
        self.commit()

    def commit(self):
        if self.connection:
            self.connection.commit()

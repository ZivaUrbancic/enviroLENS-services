import psycopg2


class PostgresQL:
    """Connection to the PostgresQL database

    Args:
        host (str): The host address. (Default "127.0.0.1")
        port (str): The port number. (Default "5432")

    """

    def __init__(self, host="127.0.0.1", port="5432"):
        self.host = host
        self.port = port


    def db_query(self,query_words): 
        """ From database returns list of dictionaries containing document IDs and text. Documents contain at least one query word.
        Args:
            query_words(list): List of query words
        Returns: 
            documents(list): list of dictionaries containing document IDs and text"""
        output = '|'.join(query_words)
       
        documents=  self.execute("""
                 SELECT document_id, fulltext_cleaned FROM documents
                 WHERE to_tsvector('english', fulltext_cleaned) @@ to_tsquery( %s )""",(output, ))

        return(documents)

    def db_return_docs_metadata(self, metric_fn_output):
        """From database returns document metadata.
        Args:
            metric_fn_output(list): List of tuples (output of metric function). First tuple element is document ID, second id document metric score.
        Returns: 
            docs_metadata(list): list of dictionaries containing document source, date, title, celex_num and full text link (docs sorted by relavance)."""

        ids = []

        for tupl in metric_fn_output:
            ids.append(tupl[0])
        if ids == []:
            raise Exception('No relavant documents for the given query.')
        t = tuple(ids)
        SQL = """SELECT document_id,document_source, date, title, celex_num, fulltextlink FROM documents WHERE document_id IN {}""".format(t)
        docs_metadata = self.execute(SQL)
        metadata_sorted = [None] * len(ids)
        for elt in docs_metadata:
            id_ = elt.get('document_id')
            position = ids.index(id_)
            metadata_sorted[position] = {k:elt[k] for k in ('document_source', 'date', 'title', 'celex_num', 'fulltextlink')}
        return metadata_sorted

    def db_nb_docs(self):
        SQL = """
                SELECT COUNT(*) FROM documents;"""
        leng = self.execute(SQL)
        leng = leng[0].get('count')
        return(leng)

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

            # store the connection cursor
            self.cursor = self.connection.cursor()

        except (Exception, psycopg2.Error) as error:
            # notify the user about the error
            print ("Error while connecting to PostgreSQL", error)
            self.cursor = None


    def disconnect(self):
        """Disconnect the postgresql connection to the database"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgresQL connection ended")


    def execute(self, statement, *placeholder_values):
        """Execute the provided statement

        Args:
            statement (str): The postgresql statement to be executed.

        Returns:
            list: a list of tuples containing the postgresql records.

        """
        if self.cursor is None:
            raise Exception("The connection is not established")
        elif placeholder_values:
            if len(placeholder_values) == 1:
                self.cursor.execute(statement, placeholder_values)
                num_fields = len(self.cursor.description)
                field_names = [i[0] for i in self.cursor.description]
                return [{ field_names[i]: row[i] for i in range(num_fields) } for row in self.cursor.fetchall()]
            else:
                raise Exception("Too much arguments")
        else:
            self.cursor.execute(statement)
            num_fields = len(self.cursor.description)
            field_names = [i[0] for i in self.cursor.description]
            return [{ field_names[i]: row[i] for i in range(num_fields) } for row in self.cursor.fetchall()]

    # TODO: add project specific routes
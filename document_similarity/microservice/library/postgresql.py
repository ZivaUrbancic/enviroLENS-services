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

    def retrieve(self, name_of_table, names_of_columns='*', constraints=None, user_input=None):
        """Returns values of columns with names in 'names_of_columns' that satisfy given constraints.

        Args:
            name_of_table (string): Name of the table we want to retrieve from.
            names_of_columns (string): List of names of columns we want to retrieve from, separated by a comma.
                (Default='*')
            constraints (string): SQL statement describing the constraints on our query. Example:
                '''ORDERED BY name_of_column DESC'''
                (Default = None)
            user_input (tuple(miscellaneous)): values to be formatted into the statement. It has to be None when
                'constraints' is None. (Default: None)

        Returns:
            (json object): json object with retrieved data.
        """


        if constraints is None:
            statement = """
            SELECT {} FROM {};
            """
            return self.execute(statement.format(names_of_columns, name_of_table))
        else:
            statement = """
            SELECT {} FROM {}
            """ + constraints + ";"
            if user_input is None:
                return self.execute(statement.format(names_of_columns, name_of_table))
            else:
                return self.execute(statement.format(names_of_columns, name_of_table), (*user_input,))

    def insert(self, name_of_table, values, user_input):
        """Inserts values to a table.

        Args:
            name_of_table (string): Name of the table we want to insert into.
            values (string): SQL code describing values to insert. Example:
                '''VALUES (%s, %s)'''
            user_input (list(miscellaneous)): values to be formatted into the statement.
        """

        statement ="""
            INSERT INTO {}
            """ + values + ";"
        self.execute(statement.format(name_of_table), (*user_input,))
        self.commit()

    def commit(self):
        if self.connection:
            self.connection.commit()


    # TODO: add project specific routes

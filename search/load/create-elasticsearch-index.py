from elasticsearch import Elasticsearch
from ..search.library.postgresql import PostgresQL
from ..search.config import config


if __name__=='__main__':
    database = config.ProductionConfig.DATABASE["database"]
    password = config.ProductionConfig.DATABASE["password"]

    print("Establish connection")
    # prepare postgresql connection
    pg = PostgresQL()
    pg.connect(database, password)
    # prepare elasticsearch connection
    print("Prepare elasticsearch index")
    es = Elasticsearch()
    # delete the envirolens index, if existing
    es.indices.delete(index='envirolens', ignore=[400, 404])
    # create a new, fresh index
    es.indices.create(index='envirolens', ignore=400, body={
        "mappings": {
            "properties": {
                "document_id": { "type": "keyword" },
                "title": { "type": "text" },
                "abstract": { "type": "text" },
                "fulltext": { "type": "text" },

                "link": { "type": "keyword" },

                "category": { "type": "keyword" },
                "date": { "type": "date" },

                "source": { "type": "keyword" },
                "status": { "type": "text" },
                "celex": { "type": "keyword" },

                "named_entities": {
                    "type": "nested",
                    "properties": {
                        "name": { "type": "keyword" },
                        "type": { "type": "keyword" }
                    }
                },

                "wikipedia": {
                    "type": "nested",
                    "properties": {
                        "name": { "type": "text" },
                        "cosine": { "type": "float" },
                        "pagerank": { "type": "float" },
                        "lang": { "type": "keyword" },
                        "url": { "type": "keyword" }
                    }
                },

                # "informea" is an array of strings
                # "keywords" is an array of strings
                # "languages" is an array of strings
            }
        }
    });

    print("Get documents from postgres")
    # get the documents from the database
    statement = """
        WITH KEYWORDS AS (
            SELECT
                document_id,
                array_agg(keyword) AS keywords
            FROM document_keywords
            GROUP BY document_id
        ),
        LANGUAGES AS (
            SELECT
                document_id,
                array_agg(language) AS languages
            FROM document_languages
            GROUP BY document_id
        ),
        WIKIPEDIA AS (
            SELECT
                document_id,
                json_agg(json_build_object('name', wikipedia_term, 'cosine', cosine, 'pagerank', pagerank, 'lang', w.language, 'url', w.url)) AS wikipedia
            FROM wikipedia_annotations
            LEFT JOIN wikipedia_concepts w ON w.concept_name = wikipedia_annotations.wikipedia_term
            GROUP BY document_id
        ),
        INFORMEA AS (
            SELECT
                document_id,
                array_agg(DISTINCT o.term ORDER BY o.term) AS informea
            FROM ontology_annotations
            LEFT JOIN ontology_terms o ON o.term = ontology_annotations.term
            GROUP BY document_id
        ),
        NAMED_ENTITIES AS (
            SELECT
                document_id,
                json_agg(json_build_object('name', ne.entity_name, 'type', ne.type)) AS named_entities
            FROM ne_annotations
            LEFT JOIN named_entities ne ON ne.entity_name = ne_annotations.named_entity
            WHERE ne.type IN ('PERSON', 'LOCATION', 'ORGANIZATION', 'MISC')
            GROUP BY document_id
        )

        SELECT
            d.document_id,
            d.title,
            d.abstract,
            d.fulltext_cleaned AS fulltext,
            d.fulltextlink AS link,

            d.date,

            d.document_source AS source,
            d.status,
            d.celex_num AS celex,

            d.publisher,
            d.referencenumber AS reference_number,

            ne.named_entities AS named_entities,

            w.wikipedia AS wikipedia,

            i.informea AS informea,
            k.keywords AS keywords,
            l.languages AS languages
        FROM documents d
        LEFT JOIN KEYWORDS k ON k.document_id = d.document_id
        LEFT JOIN LANGUAGES l ON l.document_id = d.document_id
        LEFT JOIN WIKIPEDIA w ON w.document_id = d.document_id
        LEFT JOIN INFORMEA i ON i.document_id = d.document_id
        LEFT JOIN NAMED_ENTITIES ne ON ne.document_id = d.document_id
        ORDER BY d.document_id DESC;
    """

    documents = pg.execute(statement)
    print("Number of documents", len(documents))

    print("Populate elasticsearch index")
    count = 1
    # send the documents to the index
    for document in documents:
        if "date" in document:
            # format the date value
            date = document["date"].split("/")
            # fix date format
            document["date"] = "{}-{}-{}".format(date[2], date[1], date[0])

            document["named_entities"] = document["named_entities"][:10000] if document["named_entities"] else None
            document["wikipedia"] = document["wikipedia"][:10000] if document["wikipedia"] else None
            document["informea"] = document["informea"][:10000] if document["informea"] else None
            document["keywords"] = document["keywords"][:10000] if document["keywords"] else None
            #document["languages"] = document["languages"][:10000] if document["languages"] else None

        es.index(index="envirolens", id=document["document_id"], body=document)
        if count % 1000 == 0:
            print("Number of indexed documents:", count)
        count = count + 1

    print("Refresh elasticsearch index")
    # refresh the index
    es.indices.refresh(index="envirolens")


    print("Done!")




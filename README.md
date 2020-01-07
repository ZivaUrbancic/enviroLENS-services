# TEXT EMBEDDING MICROSERVICE

Main repository for text embedding microservice. Inside this repository you can find:
* document_retrieval microservice
* document_similarity microservice
* text_embeddings microservice 
* the main microservice that will connect all of the above components

## HOW TO SETUP:

You will run each service separately. You can then use each service for themself or use the ENTRYPOINT microservice that connects all of the mentioned microservices. Here you will find instructions how to set up each of them.

You may want to create separate virtual environments for each of the microservices or you can create one for all of them. It is advisable to use virtual environments if you are developing multiple projects with Python since the dependencies can clash between eachother. (Suppose one project only supports numpy < 1.0 and the other needs numpy=1.5).

To create a virtual environment navigate to the desired directory (usually the main folder of the repository) and write 
`python -m venv venv`  
To activate this virtual environment navigate into venv/Scripts and then execute `activate`.
To deactivate a virtual environment execute `deactivate`.

You can see that your virtual environment is being used if you see __(venv)__ before the command line.

### DOCUMENT RETRIEVAL MICROSERVICE

* Activate virtual environment if you wish to do so
* Navigate into DOCUMENTRETRIEVAL folder
* run `pip install -r requirements.txt`
* Navigate into documentRetrieval/config folder
* Create `.env` file and inside define the following variables:
```
PROD_PG_DATABASE={name_of_the_db}
PROD_PG_PASSWORD={password}

DEV_PG_DATABASE={name_of_the_db}
DEV_PG_PASSWORD={pasword}
```
* Navigate into documentRetrieval folder and run the service with:   
`python -m main start -H localhost -p 4100`   
If you want you can also run the service on custom host and port.

### DOCUMENT SIMILARITY MICROSERVICE

* Activate virtual environment if you wish to do so
* Navigate into DOCUMENTSIMILARITY folder
* run `pip install -r requirements.txt`
* Navigate into microservice/config folder
* Create a `.env` file with the following variables
```
PROD_DATABASE_NAME = 
PROD_DATABASE_USER = 
PROD_DATABASE_PASSWORD = 
PROD_TEXT_EMBEDDING_URL = 

DEV_DATABASE_NAME = 
DEV_DATABASE_USER = 
DEV_DATABASE_PASSWORD = 
DEV_TEXT_EMBEDDING_URL = 
```
* Navigate into back microservice folder and run the service with   
`python -m main start -H localhost -p 4200`   
You can also use custom host and port.

__TODO__ : Here will be the instructions on how to set up each component and how to run each component.


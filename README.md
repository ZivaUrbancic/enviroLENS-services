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

__TODO__ : Here will be the instructions on how to set up each component and how to run each component.


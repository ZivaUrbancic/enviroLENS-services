:: Activating document retrieval microservice

start cmd /k "venv\Scripts\activate.bat && cd DOCUMENTRETRIEVAL && python -m documentRetrieval.main start -H localhost -p 4100"
start cmd /k "venv\Scripts\activate.bat && cd DOCUMENTSIMILARITY && python -m microservice.main start -H localhost -p 4200"
start cmd /k "venv\Scripts\activate.bat && cd TEXTEMBEDDING && python -m text_embedding.main start -H localhost -p 4001 -mp ./data/embeddings/wiki-en-small-10k.vec -ml en" 
start cmd /k "venv\Scripts\activate.bat && cd ENTRYPOINT && python -m microservice.main start -H localhost -p 4500 -teh localhost -tep 4001 -drh localhost -drp 4100 -dsh localhost -dsp 4200" 

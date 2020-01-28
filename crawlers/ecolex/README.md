# DATA CRAWLER - ECOLEX

Inside this directory are the tools that we will use to extract data from [ecolex] (ecolex.org).

## HOW TO USE

* First check how many pages of search results for documents are there on ecolex. Each page is showing up to 20 results and at the time of writting there are around 620 pages for Slovenia related documents and around 10640 pages of all documents. If there are more pages than written above then do the following:   
    
    * Open `get_main_links.py`
    * Inside the script edit the number of pages (variable name `pages`)

* You need to install some libraries (`requests` and `BeatifulSoup`). You can install them separately or just run   
```
pip install -r requirements.txt
```

To start extracting the data open `start_crawling.py` in the editor.

* Set the parameter `GET_SLOVENIA_RELATED_DOCUMENTS` to **True** if you want to get only Slovenia related documents or set it to **False** if you want to collect all documents
* Set the parameter `THREADS` to the number of threads on which you want to run the crawler. It is advised not to use too many threads since you will be making too many requests to their service and you may get banned.

* To start crawling just run `start_crawling.py`

## FORMAT OF EXTRACTED DATA

For each document a new **JSON** file will be created. Depending on type of the document it will be saved in the appropriate subdirectory:

    * treaty decisions   
    * legislation   
    * treaty  
    * jurisprudence  
    * literature

Data from a single document will be saved into a file with name `{document_name}.json`.

Inside the JSON file will be a single dictionary having different property names as keys and corresponding values as values. If the property does not exist for a particular document, its value will be shown as `None`.

Properties vary from document type to document type, some of the most common ones are:

* 'category' - (treaty decision, legislation, ...)
* 'name' - name of the document
* 'documentType' - (treaty decicisions, regulation, ...)
* 'referenceNumber'
* 'date'
* 'sourceName' -  name of the source
* 'sourceLink' - link to the source
* 'stats' - status of the document (pending, approved, ...)
* 'subject' - subjects the document covers
* 'keyword' - list of keywords 
* 'treatyName'
* 'treatyLink'
* 'meetingName'
* 'meetingLink'
* 'website'
* 'abstract' - whole content or brief explanation of the document
* 'fullTextLink' - link to the complete text of the document
* 'Country/Territory'
* 'geographicalArea' 
* 'entryIntoForceNotes'
* 'references' -
    * Each reference has its main type (Amends, Implements, Implemented by, ...)
    * value under key 'references' is another dictionary with keys (Amends, Implements, ...) and values list of references. 
    * Each reference here has a similar structure as described above 
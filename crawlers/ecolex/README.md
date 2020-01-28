# DATA GRABBER

Inside this directory are the tools that we will use to extract data from [ecolex] (ecolex.org).

## HOW TO USE

First check how many pages of search results for documents are there on ecolex. Each page is showing up to 20 results and at the time of writting there were a bit less than 620 pages for Slovenia related documents and a bit less than 10640 pages for all documents. 
If there are more pages than written above you will have to change that. To do that:

* Open **get\_main\_links.py**
* Inside the function **get\_main\_links()** edit the number of pages

To start extracting the data open main.py

Set the parameter GET\_SLOVENIA\_RELATED_DOCUMENTS to True if you want to get only Slovenia related documents. 

Run main.py

## FORMAT OF EXTRACTED DATA

For each document a new JSON file will be created. Depending on type of the document it will be saved in the appropriate subdirectory (treaty decisions / legislation).
Data from a single document will be saved into a file with name **((document name)).json**.

Inside the JSON file will be a single dictionary having different property names as keys and corresponding values as values. If the property does not exist for a particular document, its value will be shown as **None**.

Properties are:

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
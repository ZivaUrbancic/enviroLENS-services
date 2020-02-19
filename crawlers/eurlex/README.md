# EURLEX CRAWLER

Inside this folder you can find the scripts with which you can collect documents from `EUR-LEX.com`. You are able to select which documents you want to collect and in which languages.

Almost all of the document on their webpage are uniquely identified with its *CELEX NUMBER*. Therefore knowing the celex number, gives us an easy way to access the document (we just need to change the CELEX parameter of the URL to the one we want.)

The script works in the following way: First we crawl eurlex website and collect any celex numbers that we encounter. In the second part we iterate through all of the collected celex numbers and extract its data.

## How to use:

- You can run the script with `Python` versions 3.* + 
- First install the required dependencies with   
`pip install -r requirements.txt`
- The next step is to collect celex numbers. To do so:
    - Open up the `crawling_through_years_multithreading.py` in the editor
    - scroll down to the `__main__` section
    - Set up the `NUMBER_OF_THREADS` to specify on how many threads you want the script to run. Dont exagarate. Setting this too high might lead to their website banning your IP address.
    - Set up the `START_YEAR` and `END_YEAR` to tell the script to collect all of the celex numbers for the documents from ranging from `START_YEAR` to `END_YEAR`.
    - If you only wish to collect celex numbers for few specific years, set the following variable to the years you wish to crawl.   
    ```
    years = [1903, 1928, 1955] # For example if we want to crawl years 1903, 1928 and 1955
    ```

    - Collected celex numbers wil be saved into `celex_nums/` directory, each year into its separate **JSON** file.

    - run `crawling_through_years_multithreading.py` and wait :)

- To start collecting the documents data first open up `collect_celex_documents.py`
    - You have the option to set the following parameters:
        - `NUMBER_OF_THREADS` (the number of threads you want to use within the script)
        - `RELOAD`, if set to `True` you will automatically try to re-collect every document from their webpage. If set to `False`, the script will skip the documents that are already collected.
        - `LANGUAGES`, write the 2-character language identifiers into this list and the script will try to collect documents in all of the specified languages (they do not necessarily exist). For example `['EN', 'SI']` would try to collect all of the documents in english and in slovenian language.
        You can set this parameter to `None` and the script will automatically look for all of the available languages for the given document and collect its data in all languages.
    
    - When you are done, simply run the script `collect_celex_documents.py`

    The **JSON** files will be saved into `files/{2-character-language-identifier}` folder.


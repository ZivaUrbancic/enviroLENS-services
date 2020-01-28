import re
import requests
from time import time

def get_main_links(filterSLO=True):
    """
    Function that will extract all the links to documents from 'ecolex.org' and save them into a file.

    Parameters:
        filterSLO : boolean
                Set to True we will extract links only for documents that are relevant to Slovenia
                and save them into file 'main_links_SLO.txt'
                Set to False we will extract all the links and save them into file 'main_links_ALL.txt'
    
    Returns 
        None
    """

    # Link to the documents that are relevant for Slovenia, currently there are around 620 pages.
    # Each page has links to 20 documents.
    LINK_SLO = r'https://www.ecolex.org/result/?xcountry=Slovenia&page='

    # Link to all the documents. Currently there are about 10640 pages 
    # Each page has links to 20 documents.
    LINK_ALL = r'https://www.ecolex.org/result/?page='

    if filterSLO:
        filename = 'main_links_SLO.txt'
        # NUMBER OF PAGES WHEN WE FILTER FOR SLOVENIA RELEVANT DOCUMENTS
        pages = 620
        link = LINK_SLO
    else:
        filename = 'main_links_ALL.txt'
        # NUMBER OF PAGES 
        pages = 10640
        link = LINK_ALL

    with open(filename, 'w') as file_links:

        regex_link = re.compile(r'search-result-title">\s*<a href="(.*?)"')

        start_time = time()

        for page in range(1, pages + 1):
            page_link = link + str(page)

            open_page = requests.get(url=page_link)
            html_text = open_page.text

            hits = re.findall(regex_link, html_text)

            for hit in hits:
                file_links.write(hit + '\n')

            if page % 20 == 0:
                print("Successfully downloaded {}/{} pages. Time taken:".format(page, pages), round(time() - start_time, 6))

if __name__ == '__main__':
    get_main_links(filterSLO=True)



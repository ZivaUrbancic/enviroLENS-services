import re
import requests
from time import time

def get_main_links(filterSLO=True):
    """
    Function that will extract all the links to documents from 'ecolex.org' and save them into a file.

    :filterSLO:     Set to True we will extract links only for documents that are relevant to Slovenia
                    and save them into file 'main_links_SLO.txt'
                    Set to False we will extract all the links and save them into file 'main_links_ALL.txt'

    returns None
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

    file_links = open(filename, 'w')

    reLink = re.compile(r'search-result-title">\s*<a href="(.*?)"')

    start_time = time()

    for page in range(1, pages + 1):
        page_link = link + str(page)

        openpage = requests.get(url=page_link)
        html_text = openpage.text

        hits = re.findall(reLink, html_text)

        for hit in hits:
            file_links.write(hit + '\n')

        if page % 20 == 0:
            print(page, round(time() - start_time, 6))

    file_links.close()


if __name__ == '__main__':
    get_main_links(False)



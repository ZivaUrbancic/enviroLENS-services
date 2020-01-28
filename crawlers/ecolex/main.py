from get_main_links import get_main_links
import get_content_legislation
import get_content_treaty_decisions
import get_content_jurisprudence
import get_content_treaties
import get_content_literature
import os
import time
import re

# PARAMETERS:

GET_SLOVENIA_RELATED_DOCUMENTS = False
PART = 0

def main():

    filterSLO = False
    
    if GET_SLOVENIA_RELATED_DOCUMENTS:
        filterSLO = True
        if 'main_links_SLO.txt' not in os.listdir():
            get_main_links(True)
    
    else:
        if 'main_links_ALL.txt' not in os.listdir():
            get_main_links(False)
    
    success = {
        'treaty' : 0,
        'decision' : 0,
        'legislation' : 0,
        'court-decision' : 0,
        'literature' : 0,
    }

    total = {
        'treaty' : 0,
        'decision' : 0,
        'legislation' : 0,
        'court-decision' : 0,
        'literature' : 0,
    }

    total_files = 0

    # Names of the files inside which links are saved
    linksALL = 'main_links_ALL_part' + str(PART) + '.txt'
    linksSLO = 'main_links_SLO.txt'

    # Comment out this line, if you want to extract data for all slovenian documents.
    # This was made for testing to check whether all functions are working properly. 
    ## linksSLO = 'main_links_SLO_sample.txt'

    if filterSLO:
        links = open(linksSLO, 'r')
    else:
        links = open(linksALL, 'r')
    
    START_TIME = time.time()

    # We will only make atmost 3 requests to ecolex per second. With this variable we will check whether enough time has passed
    # since the last request
    checkpoint = START_TIME

    for line in links:
        total_files += 1
        url = line.strip()
        
        #: Here we check which is the type of the document
        rtype = re.compile(r'\/details\/(.*?)\/')
        doc_type = re.findall(rtype, url)[0]

        try:
            total[doc_type] += 1

            if doc_type == 'treaty':
                get_content_treaties.get_content(url, print_data=False)
            elif doc_type == 'legislation':
                get_content_legislation.get_content(url, print_data=False)
            elif doc_type == 'decision':
                get_content_treaty_decisions.get_content(url, print_data=False)
            elif doc_type == 'literature':
                get_content_literature.get_content(url, print_data=False)
            elif doc_type == 'court-decision':
                get_content_jurisprudence.get_content(url, print_data=False)
            else:
                print('I SHALL NOT BE HERE.')
            
            success[doc_type] += 1

        except:
            print('FAIL', url)
        
        if time.time() - checkpoint < 0.3:
            time.sleep(0.3)
        
        checkpoint = time.time()

        if total_files % 100 == 0:
            print(success)
            print(total)
            print(time.time() - START_TIME)
    
    print(success)
    print(total)

        

if __name__ == '__main__':
    
    for p in range(1, 11):
        PART = p
        main()
        print('PARTS', p, 'successfully taken!')
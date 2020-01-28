from get_main_links import get_main_links
import get_content_legislation
import get_content_treaty_decisions
import get_content_jurisprudence
import get_content_treaties
import get_content_literature
import os
import time
import re

import threading
from collections import deque

# PARAMETERS:

GET_SLOVENIA_RELATED_DOCUMENTS = True
THREADS = 5

class Worker(threading.Thread):

    def __init__(self, queue, name, successful, total, start_time):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.successful = successful
        self.total = total
        self.start_time = start_time

    def run(self):

        while True: # Until we run out of links

            queue_length = len(self.queue)
            if queue_length == 0:
                break

            # Check to see how we are progressing
            if queue_length % 100 == 0:
                print('{} documents remaining. Time taken: '.format(queue_length), time.time() - self.start_time)

            suffix_url = self.queue.popleft()

            # Here we check which is the type of the document
            regex_type = re.compile(r'\/details\/(.*?)\/')
            document_type = re.findall(regex_type, suffix_url)[0]

            type_to_folder_map = {
                "decision" : "treaty decisions",
                "legislation" : "legislation",
                "treaty" : "treaty",
                "literature" : "literature",
                "court-decision" : "jurisprudence"
            }

            if suffix_url in os.listdir(type_to_folder_map[document_type]):
                continue
            
            try:
                self.total[document_type] += 1

                if document_type == 'treaty':
                    get_content_treaties.get_content(suffix_url, print_data=False)
                elif document_type == 'legislation':
                    get_content_legislation.get_content(suffix_url, print_data=False)
                elif document_type == 'decision':
                    get_content_treaty_decisions.get_content(suffix_url, print_data=False)
                elif document_type == 'literature':
                    get_content_literature.get_content(suffix_url, print_data=False)
                elif document_type == 'court-decision':
                    get_content_jurisprudence.get_content(suffix_url, print_data=False)
                else:
                    print('I SHALL NOT BE HERE.')
                
                self.successful[document_type] += 1

            except Exception as e:
                print('FAIL', suffix_url)
                print(e)
            
            # We add a sleep timer in order not to spam their server too hard.
            # Each worker will sleep for a second after each task.
            time.sleep(1)


def crawl():

    filterSLO = False
    
    if GET_SLOVENIA_RELATED_DOCUMENTS:
        filterSLO = True
        if 'main_links_SLO.txt' not in os.listdir():
            print('File "main_links_SLO.txt" not found.')
            print('Started collecting document links from ECOLEX.')
            get_main_links(filterSLO=True)
    
    else:
        if 'main_links_ALL.txt' not in os.listdir():
            print('File "main_links_ALL.txt" not found.')
            print('Started collecting document links from ECOLEX.')
            get_main_links(filterSLO=False)
    
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


    # Names of the files inside which links are saved
    linksALL = 'main_links_ALL.txt'
    linksSLO = 'main_links_SLO.txt'

    # Comment out this line, if you want to extract data for all slovenian documents.
    # This was made for testing to check whether all functions are working properly. 
    # linksSLO = 'main_links_SLO_sample.txt'

    filename = linksSLO if filterSLO else linksALL

    document_queue = deque()

    with open(filename, 'r') as infile:

        for url_suffix in infile:
            document_queue.append(url_suffix.strip())
    
    total_files = len(document_queue)

    START_TIME = time.time()

    workers = []

    for worker_id in range(THREADS):
        worker = Worker(document_queue, worker_id, success, total, START_TIME)
        worker.start()
        workers.append(worker)
    
    for worker in workers:
        worker.join()
    
    print('Crawling finished!')
    print('Total time taken: {0:.2f}'.format(time.time() - START_TIME))
    print('Total number of documents to be collected:', total_files)
    print('Success rate by categories: ')
    for document_type in success:
        print('{} -> {}/{}'.format(document_type, success[document_type], total[document_type]))
        
if __name__ == '__main__':
    crawl()
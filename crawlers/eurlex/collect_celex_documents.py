import os
import time
import json
import threading
from collections import deque
from get_content import get_available_languages, collect_data

# Set this to True if you wish to rewrite all of the current collected documents. Meaning if the file of the document
# already exist, force the new extraction and overwrite the current file with the new data.

RELOAD = False

# Set the languages in which you want to download the documents. For example 
# LANGUAGES = ["EN", "DE"] would collect all the documents in english and german language.
# If you want to collect document in all of its availables languages, set LANGUAGES = None

LANGUAGES = ['EN']

# Set the number of threads. More threads will speed up the crawling but you will also spam their server harder
# and you might get banned.

NUMBER_OF_THREADS = 10

class Worker(threading.Thread):

    def __init__(self, queue, name, language_pack, working_time):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.language_pack = language_pack
        self.time = working_time
    
    def run(self):

        while True:

            queue_length = len(self.queue)

            if queue_length == 0:
                break

            if queue_length % 10 == 0:
                print('{} documents left in this batch. Time passed : {:.2f}'.format(queue_length, time.time() - self.time))

            celex_number = self.queue.popleft()
            try:
                collect_data(celex_number, languages=self.language_pack)
            except Exception as e:
                print('There was an error at {}'.format(celex_number))
                print(e)
        
        print('Worker {} finished his job. Bye!'.format(self.name))

if __name__ == '__main__':
    
    START_TIME = time.time()

    # Navigate into celex_nums directory and load up all collected celex numbers
    celex_numbers_collection = set()
    current_path = os.getcwd()
    celex_nums_path = os.path.join(current_path, 'celex_nums')

    for f in os.listdir(celex_nums_path):
        with open(os.path.join(celex_nums_path, f), 'r') as infile:
            celex_by_year = json.load(infile)
            celex_numbers_collection = celex_numbers_collection.union(set(celex_by_year))
    
    # We load up all of the currently downloaded documents. By default we are checking into
    # 'EN' directory since most likey we are collecting documents in english. Just set the 
    # already_collected_files = set() if you want to forcefully recollect all of the documents or 
    # collect documents in other languages or change the script in some other way.
    try:
        already_collected_files = set(os.listdir('files/EN'))
    except:
        already_collected_files = set()
    
    # We will work in rounds of 200 documents.
    while len(celex_numbers_collection) > 0:

        # We create a working queue.
        q = deque()

        for _ in range(200):
            
            number_candidate = celex_numbers_collection.pop()
            filename = number_candidate + '_EN.json'

            if RELOAD:
                q.append(number_candidate)
            elif filename not in already_collected_files:
                q.append(number_candidate)

            if len(celex_numbers_collection) == 0:
                break
        
        workers = []
        for i in range(NUMBER_OF_THREADS):
            worker = Worker(q, i, LANGUAGES, START_TIME)
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()

        print('One Batch is done. Time needed : {} - documents left : {}'.format(round(time.time() - START_TIME, 2), len(celex_numbers_collection)))

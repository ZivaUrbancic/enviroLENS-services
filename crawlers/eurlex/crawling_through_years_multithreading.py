"""
Script that will with multiple threads collect all of the celex numbers that are available on
EURLEX webpage. Each document is uniquely represented with its celex number so having celex numbers
gives us an easy access to all of the documents on the website.

Scroll below to the line 
```
if __name__ == '__main__':
```
to set up the parameters of the crawler.
"""

from crawl_for_celex_numbers import get_celex_numbers
import threading
import time
from collections import deque

class Worker(threading.Thread):

    def __init__(self, queue, number, working_time):
        threading.Thread.__init__(self)
        self.queue = queue
        self.number = number
        self.time = working_time
    
    def run(self):

        while True:

            if len(self.queue) == 0:
                break
            
            #: We give thread a task
            year_to_crawl = self.queue.popleft()

            #: Workers starts collecting celex numbers for particular task (year)
            get_celex_numbers(year_to_crawl)
            print('Worker {} has completed year {}. Time passed {}'.format(self.number, year_to_crawl, round(time.time() - self.time, 6)))

        print("Worker {} is shutting down. Bye!".format(self.number))

if __name__=='__main__':

    # Choose number of threads that you want to use. Do not use too many since it may spam their 
    # server too much and you might get banned.
    NUMBER_OF_THREADS = 5

    # The script will crawl for celex number from {START_YEAR} and all the years up to {END_YEAR}
    START_YEAR = 1900
    END_YEAR = 2020
    years = [year for year in range(START_YEAR, END_YEAR + 1)]
    # If you only want to crawl few specific years, uncomment the line below:
    years = [1903, 1928, 1955]

    year_queue = deque()

    for year in years:
        year_queue.append(year)

    working_time = time.time()
    workers = []
    for i in range(NUMBER_OF_THREADS):
        worker = Worker(year_queue, i, working_time)
        worker.start()
        workers.append(worker)
    

    # We wait for all the workers to finish
    for worker in workers:
        worker.join()
    
    print('Celex number are collected. Time needed : {}.'.format(round(time.time() - working_time, 6)))


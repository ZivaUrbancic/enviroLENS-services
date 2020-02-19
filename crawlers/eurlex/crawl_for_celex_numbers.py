import requests
import time
import re
import os
import json

def save_crawler_config(year, page):
    """
    Save the current year and current page into a json file. So the next time we run the script
    we will know from which points onwards we should continue our crawling.

    Parameters:
        year : int 
        page : int
    
    Returns
        None
    """

    with open('crawler_config.json', 'w') as outfile:
        json.dump(
            {
                'year' : year,
                'page' : page
            },
            outfile,
            indent=2
        )

def save_celex_numbers(celex_numbers, year):
    """
    Saves current celex numbers into json file. Since the script will take long time 
    to execute it is better to make intermediate copies.

    Parameters:
        celex_numbers : list of strings
            list of celex numbers
        year : int
            year of the documents for the given celex numbers
    """

    current_path = os.getcwd()
    if 'celex_nums' not in os.listdir(os.getcwd()):
        os.mkdir(os.path.join(current_path, 'celex_nums'))

    with open('celex_nums\\' + str(year) + '_celex_numbers.json', 'w') as outfile:
        json.dump(list(celex_numbers), outfile, indent=1)

def get_celex_numbers(starting_year):
    """
    Script that will start crawling the EURLEX page for documents from specific year. It will
    collect and save all of the celex numbers that it sees. The celex numbers will be saved into
    `celex_nums` directory.

    Note: We need to crawl the eurlex website by filtering through years since it is only possible for given query
    to look at first 10000 pages. Since there are more documents than that, we need to filter by some smaller subset 
    and iterate over all of those subsets.

    Parameter:
        starting_year : int
            year for which we want to find the celex numbers

    Returns
        None
    """

    START_TIME = time.time()

    current_celex_numbers = set()

    #: Regex pattern that will find all CELEX numbers present on the page.
    regex_celex = re.compile(r'CELEX number: <\/dt><dd>(.*?)<')

    #: template URL, we need to fill it with YEAR and PAGE
    URL = 'https://eur-lex.europa.eu/search.html?&scope=EURLEX&type=quick&lang=en&DD_YEAR={}&page={}'

    #: If either of those warnings is present, we should continue our crawling on the next year rather than 
    #: the next page since we have exhausted all of the pages for the given year.
    warning_messages = ['Please choose a smaller number of pages', 'No results found']

    current_year = starting_year
    current_page = 1

    # While loop through all the pages.
    while True:

        # In order not to spam their server too hard.
        time.sleep(0.5)

        # We fill YEAR and PAGE into template URL
        url_page = URL.format(current_year, current_page)

        #: Request the page and find all celex number and add it to our collection of celex numbers
        page = requests.get(url_page)
        count_failed_requests = 0
        while page.status_code != 200:
            time.sleep(0.3)
            page = requests.get(url_page)
            count_failed_requests += 1
            if count_failed_requests > 3:
                break

        year_exhausted = False

        if page.status_code == 200:
            find_celex_nums = re.findall(regex_celex, page.text)

            for celex in find_celex_nums:
                current_celex_numbers.add(celex)

            for warning_message in warning_messages:
                if warning_message in page.text:
                    year_exhausted = True

        #: If we got a warning message, we should break our loop through pages.
        if year_exhausted:
            break
        
        current_page += 1

        #: We do intermediate saves for every 10 checked pages
        if current_page % 10 == 0:
            save_celex_numbers(current_celex_numbers, starting_year)
            print('YEAR : {} - PAGE : {} - TIME : {}'.format(current_year, current_page, round(time.time() - START_TIME, 3)))
            print('Currently found {} celex numbers for year {}.'.format(len(current_celex_numbers), starting_year))
    
    #: In the end we save our result
    save_celex_numbers(current_celex_numbers, starting_year)

if __name__ == '__main__':
    get_celex_numbers(1955)
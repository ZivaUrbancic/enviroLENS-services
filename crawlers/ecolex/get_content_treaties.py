"""
get_content(url, print_data=False) is a function that will grab the relevant data for documents of type 'TREATY'.
"""

import re
import requests
import json
from bs4 import BeautifulSoup
from helper_functions import get_value_or_none, remove_forbidden_characters, get_list_or_none

BASE_URL = r'https://www.ecolex.org'

def get_content(suffix, print_data=False):
    """
    From the page ( 'ecolex.org'+ suffix ) we grab the relevant metadata (eg. type, document Type, name, reference, number,
    date, source name and source link, status, subject, keywords, treaty name and link, meeting name and link, website, abstract,
    ...).
    The data is then saved into a dictionary with parameter names as keys and the grabbed results as the values.

    Example:

    data["category"] = "Treaty decision"
    data["name"] = "Decision XXIX_21 _ Membership of the Implementation Committee"

    In the end the dictionary is saved into a json file named (data["name"] without forbidden characters and 
    length limited to 100).json

    Parameters:
        suffix : string
            the suffix of the url from which we are extracting the data. The suffix string is everything that comes 
            after the 'ecolex.org'

        print_data : boolean 
            Optional parameter that is by default set to False. In case it is set to True, the function will at the end 
            also print what it managed to extract from the page.

    Returns 
        None
    """

    data = dict()
    data['URL'] = BASE_URL + suffix

    # We request the page. If the requests was successful we take the content of the page and save it into page_text
    get_page = requests.get(BASE_URL + suffix)
    if get_page.status_code != 200:
        print('Request Denied!', suffix)
    page_text = get_page.text

    #: All the relevant data about the document is saved within <article> tags.
    #: With BeautifulSoup its simple to navigate to that part of the html file.
    soup = BeautifulSoup(page_text, 'html.parser')
    important_text = str(soup.find('article'))

    #: Below are all the parameters and regex patterns that a document might have.

    string_parameters = {
        'documentType' : r'Document type.*?dd>(.*?)<',
        'fieldOfApplication' : r'Field of application.*?dd>(.*?)<',
        'date' : r'Date.*?dd>(.*)<',
        'sourceLink' : r'Source.*\s*.*\s*.*?href="(.*?)"',
        'sourceName' : r'Source.*\s*.*\s*.*?.*?>(.*?)<',
        'sourceID' : r'Source.*\s*.*\s*.*?ID:(.*)\)',
        'title' : r'Title.*\s*.*\s*.*?>(.*?)<',
        'placeOfAdoption' : r'Place of adoption.*\s*<dd>(.*?)<',
        'depository' : r'Depository.*\s*<dd>(.*)<',
        'entryIntoForce' : r'Entry into force.*\s*<dd>(.*?)<',
        'subject' : r'Subject.*\s*<dd>(.*?)<',
        'geographicalArea' : r'Geographical area.*\s*<dd>(.*?)<',
        'abstract' : r'p class="abstract">(.*)<\/p>',
        'fullTextLink' : r'Full text.*\s*.*\s*<a href="(.*?)"',
        'websiteLink' : r'Website.*\s*.*\s*<a href="(.*?)"',
        'website' : r'Website.*\s*.*\s*.*\s*.*?>(.*)<',
    }

    list_parameters = {
        'language' : r'anguage.*\s*<dd>(.*?)<',
    }

    for parameter_name, regex_pattern in string_parameters.items():
        re_pattern = re.compile(regex_pattern)
        data[parameter_name] = get_value_or_none(re_pattern, important_text)

    for parameter_name, regex_pattern in list_parameters.items():
        re_pattern = re.compile(regex_pattern)
        data[parameter_name] = get_list_or_none(re_pattern, important_text)

    data['category'] = 'treaty'

    #: NAME, type : string

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = get_value_or_none(re_name, important_text)
    if data['name'] is not None:
        data['name'] = remove_forbidden_characters(data['name'])
    else:
        print('Name of the file not found!', suffix)

    #: KEYWORDS, list of strings

    re_keywords = re.compile(r'span class="tag">(.*)<')
    data['keywords'] = re.findall(re_keywords, important_text)

    #: COUNTRY, ENTRY INTO FORCE, RATIFICATION, SIMPLE SIGNATURE. Will be saved as a list of dicionaries

    participants = soup.find('article').find('section', {'id' : 'participants'})

    data['participants'] = None
    
    if participants is not None:
        table = participants.find('table', {'class' : 'participants'}).find('tbody')

        data['participants'] = []

        for column in table.find_all('tr'):

            country_pattern = {
                'country' : r'th>(.*)<',
                'entryIntoForceDate' : r'Entry into force date">\s*(.*)',
                'ratificationDate' : r'Ratification date".*\s*(.*)',
                'simpleSignatureDate' : r'Simple signature date">\s*(.*)',
            }

            column_data = dict()

            for parameter_name, regex_pattern in country_pattern.items():
                re_pat = re.compile(regex_pattern)
                column_data[parameter_name] = get_value_or_none(re_pat, str(column))
            
            data['participants'].append(column_data)
    
    ########################################################################
    ########################################################################

    if print_data:
        for key, value in data.items():
            print(key  + ' : ' + str(value))
    
    with open('treaty\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)
"""
get_content(url, print_data=False) is a function that will grab the relevant data for documents of type 'JURISPRUDENCE'
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
        'country/Territory' : r'Country\/Territory.*\s.*<dd>(.*?)<',
        'typeOfCourt' : r'Type of court.*\s*<dd>(.*?)<',
        'date' : r'Date.*?<dd>(.*?)<',
        'sourceName' : r'Source.*\s*<dd>(.*?),',
        'sourceLink' : r'Source.*\s*.*href="(.*)"',
        'courtName' : r'Court name.*\s*<dd>(.*)<',
        'seatOfCourt' : r'Seat of court.*\s*<dd>(.*)<',
        'referenceNumber' : r'Reference number.*?<dd>(.*)<',
        'language' : r'Language.*\s*<dd>(.*)<',
        'subject' : r'Subject.*\s*<dd>(.*?)<',
        'abstract' : r'Abstract<\/dt>\s*(.*)',
        'fullTextLink' : r'Full text.*\s*.*?href="(.*?)"',
    }

    list_parameters = {
    }

    for parameter_name, regex_pattern in string_parameters.items():
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_value_or_none(re_pat, page_text)

    for parameter_name, regex_pattern in list_parameters.items():
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_list_or_none(re_pat, page_text)


    data['category'] = 'jurisprudence'

    #: NAME, type : string

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = get_value_or_none(re_name, important_text)
    if data['name'] is not None:
        data['name'] = remove_forbidden_characters(data['name'])
    else:
        print('Name of the file not found!', suffix)

    #: JUDGE, list of judges

    re_judge = re.compile(r'Judge.*?<dd>(.*?)<')
    result = get_value_or_none(re_judge, important_text)
    if result is not None:
        data['judge'] = result.split(';')

    re_keyword = re.compile(r'span class="tag">(.*?)<')
    data['keywords'] = re.findall(re_keyword, important_text)

    ########################################################################
    ########################################################################

    if print_data:
        for key, value in data.items():
            print(key  + ' : ' + str(value))
    
    with open('jurisprudence\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)


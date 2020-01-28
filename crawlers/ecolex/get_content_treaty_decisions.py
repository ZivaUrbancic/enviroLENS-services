"""
get_content(url_suffix, print_data=False) is a function that will collect the relevant data for documents of type 'TREATY DECISIONS'.
"""

import re
import requests
import json
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

    get_page = requests.get(BASE_URL + suffix)
    if get_page.status_code != 200:
        print('Request Denied!', suffix)
        #: in case request is denied, we can't do anything
    page_text = get_page.text

    #: Below are all the parameters and regex patterns that a document might have. Since the pattern can vary drastically
    #: it was easier to do for every parameter one by one.

    string_parameters = {
        'category' : r'record-icon">\s*<.*?title="(.*?)"',
        'documentType' : r'Document type<\/dt>\s?<dd>(.*?)<',
        'referenceNumber' : r'Reference number<\/dt>\s?<dd>(.*?)<',
        'date' : r'Date<\/dt>\s?<dd>(.*?)<',
        'sourceName' : r'Source<\/dt>\s?<dd>(.*?),',
        'sourceLink' : r'Source<\/dt>\s?<dd>.*?href="(.*?)"',
        'status' : r'Status<\/dt>\s?<dd>(.*?)<',
        'treatyName' : r'Treaty<\/dt>\s*<dd>\s*.*?>\s*(.*)',
        'meetingName' : r'Meeting<\/dt>\s*<dd>\s*.*\s*.*?>(.*?)<',
        'meetingLink' : r'Meeting<\/dt>\s*<dd>\s*<a href="(.*?)"',
        'website' : r'Website<\/dt>\s*<dd>\s*<a href="(.*?)"',
        'fullTextLink' : r'Full text<\/dt>\s*<dd>\s*<a href="(.*?)"',
    }

    list_parameters = {
        'subject' : r'Subject<\/dt>\s*<dd>(.*?)<',
        'country/Territory' : r'Country\/Territory<\/dt>\s*<dd>(.*?)<',
        'geographicalArea' : r'Geographical area<\/dt>\s*<dd>(.*?)<',
    }

    for parameter_name, regex_pattern in string_parameters.items():
        pattern = re.compile(regex_pattern)
        data[parameter_name] = get_value_or_none(pattern, page_text)

    for parameter_name, regex_pattern in list_parameters.items():
        pattern = re.compile(regex_pattern)
        data[parameter_name] = get_list_or_none(pattern, page_text)

    # Parameters below are special and are done separately: 

    #: NAME, type : string

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = get_value_or_none(re_name, page_text)
    if data['name'] is not None:
        data['name'] = remove_forbidden_characters(data['name'])
    else:
        print('Name of the file not found!', suffix)

    #: KEYWORD, type : list of strings

    re_keyword = re.compile(r'span class="tag">(.*?)<')
    data['keyword'] = re.findall(re_keyword, page_text)

    #: TREATY - LINK, type : string

    re_treatyLink = re.compile(r'Treaty<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['treatyLink'] = get_value_or_none(re_treatyLink, page_text)
    if data['treatyLink'] is not None:
        data['treatyLink'] = base_link + data['treatyLink']

    #: ABSTRACT, type : string
    #: At current implementation all the html tags are removed from the text. It might make sense to keep that <p> paragraph tags. 

    re_abstract = re.compile(r'Abstract<\/dt>\s*<dd>\s*<div.*?>(.*?)<\/div>')
    abstract_text = get_value_or_none(re_abstract, page_text)
    data['abstract'] = abstract_text

    ########################################################################
    ########################################################################

    if print_data:
        for key, value in data.items():
            print(key  + ' : ' + str(value))
    
    with open('treaty decisions\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)






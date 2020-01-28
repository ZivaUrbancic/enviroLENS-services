"""
get_content(url, print_data=False) is a function that will grab the relevant data for documents of type 'LEGISLATION'
"""

import re
import requests
import json
from bs4 import BeautifulSoup
from time import time
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

    #: Below are all the parameters and regex patterns that a document might have. Since the pattern can vary drastically
    #: it was easier to do for every parameter one by one.

    string_parameters = {
        'category' : r'record-icon">\s*<.*?title="(.*?)"',
        'documentType' : r'Document type<\/dt>\s?<dd>(.*?)<',
        'referenceNumber' : r'Reference number<\/dt>\s?<dd>(.*?)<',
        'date' : r'title="Date">(.*?)<',
        'sourceName' : r'Source<\/dt>\s*<dd>\s*(.*?),',
        'sourceLink' : r'Source<\/dt>\s*<dd>\s*.*\s*.*?href="(.*?)"',
        'status' : r'Status<\/dt>\s?<dd>(.*?)<',
        'treatyName' : r'Treaty<\/dt>\s*<dd>\s*.*?>\s*(.*)',
        'meetingName' : r'Meeting<\/dt>\s*<dd>\s*.*\s*.*?>(.*?)<',
        'meetingLink' : r'Meeting<\/dt>\s*<dd>\s*<a href="(.*?)"',
        'website' : r'Website<\/dt>\s*<dd>\s*<a href="(.*?)"',
        'fullTextLink' : r'Full text<\/dt>\s*<dd>\s*<a href="(.*?)"',
        'entryIntoForceNotes' : r'Entry into force notes<\/dt>\s*<dd>(.*?)<\/dd',
    }

    list_parameters = {
        'subject' : r'Subject<\/dt>\s*<dd>(.*?)<',
        'country/Territory' : r'Country\/Territory<\/dt>\s*<dd>(.*?)<',
        'geographicalArea' : r'Geographical area<\/dt>\s*<dd>(.*?)<',
    }

    for parameter_name, regex_pattern in string_parameters.items():
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_value_or_none(re_pat, page_text)
    
    for parameter_name, regex_pattern in list_parameters.items():
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_list_or_none(re_pat, page_text)

    # Those are special and are done separately:

    ###: NAME, type : string

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = get_value_or_none(re_name, page_text)
    if data['name'] is not None:
        data['name'] = remove_forbidden_characters(data['name'])
    else:
        print('Name of the file not found!', suffix)

    ###: KEYWORD, type : list of strings

    re_keyword = re.compile(r'span class="tag">(.*?)<')
    data['keyword'] = re.findall(re_keyword, page_text)

    ###: TREATY - LINK, type : string

    re_treatyLink = re.compile(r'Treaty<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['treatyLink'] = get_value_or_none(re_treatyLink, page_text)
    if data['treatyLink'] is not None:
        data['treatyLink'] = BASE_URL + data['treatyLink']

    ###: ABSTRACT, type : string
    #: In the current implementation all html tags are removed from the text. It might make sense to keep the paragraphs tags.  

    re_abstract = re.compile(r'Abstract<\/dt>\s*<dd>(.*?)<\/dd')
    abstract_text = get_value_or_none(re_abstract, page_text)

    if abstract_text is not None:

        all_tags = re.compile(r'<.*?>')
        cleaned_text = re.sub(all_tags, '', abstract_text)

        data['abstract'] = cleaned_text
    else:
        data['abstract'] = None

    ########################################################################################
    ########################################################################################

    """
    Below we are extracting the data of references of the document. Since the html structue is much more complex, this
    will be easier to do with the BeautifulSoup library.

    - All the data about the document is written inside <article> tag.
    - All the data about references is written inside <section, id='legislation-references'> tag.
    - References are grouped by their type (Amends, Implements, Implemented by, ...). Every group is saved inside <dl> tag.
    - Inside every <dl> tag, we can find the type of the group in <dt> tag, and then in every <dd> tag that follows, we can grab
      the data of each reference.

    Here we use BeautifulSoup library since with its tools we are able to navigate through html tags and structure easily.

    """

    soup = BeautifulSoup(page_text, 'html.parser')
    ref_section = soup.find('article').find('section', {'id' : 'legislation-references'})
    if ref_section is not None:
        ref_section = ref_section.find_all('dl')

    data['references'] = dict()

    if ref_section is not None:

        for type_reference in ref_section:
            tip = type_reference.dt.text
            data['references'][tip] = []

            for each_reference in type_reference.find_all('dd'):

                reftekst = str(each_reference)
                
                single_reference = dict()

                ref_string_parameters = {
                    'refLink' : r'title">\s*<.*?="(.*?)"',
                    'refName' : r'search-result-title">\s*.*\s*.*?>(.*?)<',
                    'refCountry' : r'title="Country\/Territory">(.*)<',
                    'refDate' : r'title="Date">(.*)',
                    'refSourceLink' : r'Source.*\s*.*? href="(.*?)"',
                    'refSourceName' : r'Source.*\s*.*?>(.*?)<',
                }

                for parameter_name, regex_pattern in ref_string_parameters.items():
                    re_pat = re.compile(regex_pattern)
                    single_reference[parameter_name] = get_value_or_none(re_pat, reftekst)

                re_refKeywords = re.compile(r'keywords">(.*?)<')
                single_reference['refKeywords'] = get_list_or_none(re_refKeywords, reftekst)

                data['references'][tip].append(single_reference)


    ########################################################################
    ########################################################################

    if print_data:
        for key, value in data.items():
            print(key  + ' : ' + str(value))
    
    with open('legislation\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)





"""
get_content(url, print_data=False) is a function that will grab the relevant data for documents of type 'LITERATURE'
"""

import re
import requests
from bs4 import BeautifulSoup
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

    # We request the page. If the quests was successful we take the content of the page and save it into page_text
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
        'date' : r'<dt>Date.*\s*<dd>(.*?)<',
        'sourceLink' : r'Source.*\s*.*\s*.*?href="(.*?)"',
        'sourceName' : r'Source.*\s*.*\s*.*?>(.*?)<',
        'sourceID' : r'\(ID:.*?>(.*?)<',
        'publisher' : r'Publisher.*\s*.*\s*(.*)',
        'placePublication' : r'Place of publication.*\s*.*\s*.*\s*\|(.*)',
        'ISBN' : r'ISBN.*\s*<dd>(.*?)<',
        'ISSN' : r'ISSN.*\s*<dd>(.*?)<',
        'pages' : r'Pages.*\s*<dd>(\d*)',
        'documentType' : r'Document type.*\s*<dd>(.*?)<',
        'fullTextLink' : r'Full text.*\s*.*\s*.*?href="(.*?)"',
        'website' : r'Website.*\s*.*\s*<a href="(.*?)"',
        'basin' : r'Basin.*\s*<dd>(.*?)<',
        'fieldOfApplication' : r'Field of application.*\s*<dd>(.*?)<',
        'DOI' : r'DOI.*\s*.*\s*<a href="(.*?)"',
        'journal/series' : r'Journal\/Series.*\s*<dd>\s*(.*\s*\|.*)',
    }

    list_parameters = {
        'author' : r'uthor.*\s*<dd>(.*?)<',
        'language' : r'Language.*\s*<dd>(.*?)<',
        'country/Territory' : r'Country\/Territory.*\s*<dd>(.*?)<',
        'subject' : r'Subject.*\s*<dd>(.*?)<',
        'geographicalArea' : r'Geographical area.*\s*<dd>(.*?)<',
    }

    for parameter_name, regex_pattern in string_parameters.items():
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_value_or_none(re_pat, important_text)

    for parameter_name, regex_pattern in list_parameters.items():
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_list_or_none(re_pat, important_text)

    data['category'] = 'literature'

    #: NAME, type : string

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = get_value_or_none(re_name, important_text)
    if data['name'] is not None:
        data['name'] = remove_forbidden_characters(data['name'])
    else:
        print('Name of the file not found!', suffix)

    #: KEYWORDS : list of strings
    #: Because of the html structure around keywords, we are able to extract all keywords with just re.findall(...)

    re_keyword = re.compile(r'span class="tag">(.*?)<')
    data['keyword'] = re.findall(re_keyword, important_text)

    #: ABSTRACT, type : string

    re_abstract = re.compile(r'class="abstract">(.*)')
    data['abstract'] = get_value_or_none(re_abstract, important_text)

    #: We have two types of references, one is literature references, the other is 
    #:'other references'. In each of them, data for a single reference is saved inside <dl> tag.
    #: With BeautfiulSoup we navigate into each of these <dl> tags and extract data of that reference.
    #: Data is saved into our dictionaty as follows:
    #: - Data['other_references'] = list()
    #: - for each reference we append into that list a dictionary of that reference
    #: - the dictionary is of the same structure as above

    ref_section = soup.find('article').find('section', {'id' : 'other-references'})

    if ref_section is not None:

        data['other_references'] = list()
        
        other_refs = ref_section.find_all('dl')
        for each_reference in other_refs:

            reftext = str(each_reference)

            single_reference = dict()

            ref_string_parameters = {
                'refType' : r'<dt>(.*?)<',
                'refLink' : r'result-title.*\s*.*?href="(.*)"',
                'refName' : r'result-title.*\s*.*\s*title="(.*)"',
                'refDocumentType' : r'Document type">(.*?)<',
                'refPlaceOfAdoption' : r'Place of adoption">(.*?)<',
                'refDate' : r'Date:(.*?)"',
                'refSourceID' : r'source.*\s*.*?ID:(.*?)<',
                'refSourceLink' : r'source.*\s*.*?href="(.*?)"',
                'refSourceName' : r'source.*\s*.*?href.*?>(.*?)<'
            }

            ref_list_parameters = {
                'refKeywords' : r'keywords">(.*?)<',
            }

            for parameter_name, regex_pattern in ref_string_parameters.items():
                re_pat = re.compile(regex_pattern)
                single_reference[parameter_name] = get_value_or_none(re_pat, reftext)

            for parameter_name, regex_pattern in ref_list_parameters.items():
                re_pat = re.compile(regex_pattern)
                single_reference[parameter_name] = get_list_or_none(re_pat, reftext)
            
            data['other_references'].append(single_reference)
    
    ref_section_literature = soup.find('article').find('section', {'id' : 'literature-references'})

    if ref_section_literature is not None:

        data['literature_references'] = []

        literature_references = ref_section_literature.find('dl')

        for each_reference in literature_references:

            reftext = str(each_reference)
            single_reference = dict()

            ref_string_parameters = {
                'refName' : r'result-title.*\s*.*\s*.*?>(.*?)<',
                'refLink' : r'result-title.*\s*.*?href="(.*?)"',
                'refAuthor' : r'uthor:.*\s*.*?>(.*?)<',
                'refPublishedIn' : r'details.*\s*.*?In:.*?span>(.*?)<',
                'refPublishedInWhere' : r'details.*\s*.*In.*\s*\|(.*)',
                'refPublisher' : r'Publisher.*?span>(.*)<',
                'refPublicationPlace' : r'Publication place">(.*)<',
                'refPublicationDate' : r'ublication date">(.*)<',
                'refSourceLink' : r'Source.*\s*.*?href="(.*?)"',
                'refSourceName' : r'Source.*\s*.*?>(.*?)<',
                'refSourceID' : r'result-source.*\s*.*?ID:(.*)\)',
            }

            ref_list_parameters = {
                'refCountryTerritory' : r'Territory">(.*)<',
                'refKeywords' : r'keywords">(.*)<',
            }

            for parameter_name, regex_pattern in ref_string_parameters.items():
                re_pat = re.compile(regex_pattern)
                single_reference[parameter_name] = get_value_or_none(re_pat, reftext)

            for parameter_name, regex_pattern in ref_list_parameters.items():
                re_pat = re.compile(regex_pattern)
                single_reference[parameter_name] = get_list_or_none(re_pat, reftext)

            data['literature_references'].append(single_reference)

    if print_data:
        for key, value in data.items():
            print(key  + ' : ' + str(value))

    with open('literature\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)

if __name__ == '__main__':
    tlink = r'/details/literature/marine-protected-areas-and-ocean-stewardship-a-legal-perspective-ana-093555/?type=literature&page=15'
    tlink = r'/details/literature/recognition-of-enviromental-services-in-the-icjs-first-award-of-compensation-for-international-environmental-damage-ana-093549/?type=literature&page=15'
    tlink = r'/details/literature/legal-aspects-of-land-purchasesale-disputes-in-indonesia-ana-093552/?type=literature&page=15'
    get_content(tlink, True)
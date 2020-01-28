import re
import requests
import json
from helperFunctions import get_value_or_none, remove_forbidden_characters, get_list_or_none

#: get_content(url, print_data=False) is a function that will grab the relevant data for documents of type 'TREATY DECISIONS'

base_link = r'https://www.ecolex.org'

def get_content(suffix, print_data = False):
    """
    From the page ( 'ecolex.org'+ suffix ) we grab the relevant data that is (type, document Type, name, reference, number,
    date, source name and source link, status, subject, keywords, treaty name and link, meeting name and link, website, abstract,
    ...).
    The data is then saved into a dictionary with parameter names as keys and the grabbed result as the value.

    Example:

    data["category"] = "Treaty decision"
    data["name"] = "Decision XXIX_21 _ Membership of the Implementation Committee"

    In the end the dictionary is saved into a json file named (data["name"] without forbidden characters and 
    length limited to 100).json

    :suffix:        the suffix of the url from which we are extracting the data. The suffix string is everything that comes 
                    after the 'ecolex.org'
    :print_data:    Optional parameter that is by default set to False. In case it is set to True, the function will at the end 
                    also print what it managed to extract from the page.

    returns None
    """

    data = dict()

    get_page = requests.get(base_link + suffix)
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
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_value_or_none(re_pat, page_text)

    for parameter_name, regex_pattern in list_parameters.items():
        re_pat = re.compile(regex_pattern)
        data[parameter_name] = get_list_or_none(re_pat, page_text)

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

    if abstract_text is not None:

        all_tags = re.compile(r'<.*?>')
        cleaned_text = re.sub(all_tags, '', abstract_text)

        data['abstract'] = cleaned_text
    else:
        data['abstract'] = None

    ########################################################################
    ########################################################################

    if print_data:
        for key in data:
            print(key  + ' : ' + str(data[key]))
    
    with open('treaty decisions\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    pass





import requests
import re
import json
from helper_functions import *
from bs4 import BeautifulSoup
import time
import os

LANGUAGES = [
    'BG', 'ES', 'CS', 'DA', 'DE', 'ET', 'EL', 'EN', 'FR', 'GA', 'HR', 'IT', 'LV', 'LT',
    'HU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'FI', 'SV'
]

def get_available_languages(celex_number):
    """
    Function that will take celex_number as input and return us all the languages in which this particular
    document is avaiable.

    Parameters:
        celex_number : string
            celex_number of the document
    
    Returns
        list of available languages (example : ["EN", "CS", "DE"])
    """

    url = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:{}'.format(celex_number)

    # We will redo request until we get a successful one
    # Maximum 20 failed attempts
    failed_requests_counter = 0
    page = requests.get(url)
    while page.status_code != 200:
        page = requests.get(url)
        time.sleep(1)

        failed_requests_counter += 1
        if failed_requests_counter > 20:
            return ['EN']

    page_text = page.text

    # We use BeautifulSoup to navigate to html block in which language data is written.

    soup = BeautifulSoup(page_text, 'html.parser')
    soup = soup.find('body')
    soup = soup.find('div', {'class' : 'Wrapper clearfix'})
    soup = soup.find('div', {'class' : 'container-fluid'})
    soup = soup.find('div', {'id' : 'MainContent'})
    soup = soup.find('div', {'class' : 'row row-offcanvas'})
    soup = soup.find('div', {'id' : 'documentView', 'class' : 'col-md-9'})
    soup = soup.find('div', {'class' : 'EurlexContent'})
    soup = soup.find('div', {'class' : 'panel-group'})
    soup = soup.find('div', {'id' : 'multilingualPoint'})

    available_lang_part = soup.find('div', {'id' : 'PP2Contents'})
    available_lang_part = available_lang_part.find('div', {'class' : 'PubFormats'})
    available_lang_part = available_lang_part.find('ul', {'class' : 'dropdown-menu PubFormatVIEW'})

    available_languages = []

    # <li> tags that have class name 'disabled' are the li tags of non available languages.
    for child in available_lang_part.find_all('li'):
        if 'disabled' not in child.get('class'):
            available_languages.append(child.get_text().strip())
    
    return available_languages

def get_document_data_in_fixed_language(celex_number, language='EN'):
    """
    Requests the url of a document with CELEX NUMBER = {celex_number} on eur-lex.europa.eu and extracts
    relevant information. Extracted information is saved into a dictionary and is then returned.

    Parameters:
        celex_number : string
            celex_number of the document
        langauge : string
            two character tag of the language in which we want to extract the documents information

    Returns
        dictionary of collected values
    """

    url = r'https://eur-lex.europa.eu/legal-content/{}/ALL/?uri=CELEX:{}'.format(language, celex_number)

    # We will redo requests every 1 second until we get a successful one 
    # If we will fail requests 3 times, we stop trying.
    failed_requests_counter = 0
    page = requests.get(url)
    while page.status_code != 200:
        page = requests.get(url)
        time.sleep(1)
        failed_requests_counter += 1
        if failed_requests_counter > 2:
            return {}

    page_text = page.text

    document_data = {}

    # With BeatifulSoup we quickly navigate through html structure to the part where the
    # interesting data is hidden:
    # body
    # div class="Wrapper clearfix"
    # div class="container-fluid"
    # div id="MainContent"
    # div class="row row-offcanvas"
    # div id="documentView" class="col-md-9"
    # div class="EurlexContent"
    # div class="panel-group"

    soup = BeautifulSoup(page_text, 'html.parser')
    soup = soup.find('body')
    soup = soup.find('div', {'class' : 'Wrapper clearfix'})
    soup = soup.find('div', {'class' : 'container-fluid'})
    soup = soup.find('div', {'id' : 'MainContent'})
    soup = soup.find('div', {'class' : 'row row-offcanvas'})
    soup = soup.find('div', {'id' : 'documentView', 'class' : 'col-md-9'})
    soup = soup.find('div', {'class' : 'EurlexContent'})
    soup = soup.find('div', {'class' : 'panel-group'})

    # Extracting metadata: We navigate into div id="multilingualPoint"

    metadata = soup.find('div', {'id' : 'multilingualPoint'})

    string_parameters = {
        'translatedTitle' : r'translatedTitle.*?>(.*?)<',
        'originalTitle' : r'originalTitle.*?>(.*?)<',
    }

    for parameter_name, regex_pattern in string_parameters.items():
        document_data[parameter_name] = get_value_or_none(regex_pattern, str(metadata))
    
    ## EUROVOC descriptors:

    # We find the div tag that contains the descriptor. There is no easy way to find out in which of the div tags it
    # is in. But we are able to identity the right block with the key word 'Classifications'.

    for block in metadata.find_all('div', {'class' : 'panel panel-default PagePanel'}):

        try:
            if 'Classifications' in block.text:
                descriptor_block = block.find('div', {'id' : 'PPClass_Contents'})
                descriptor_block = descriptor_block.find('div', {'class' : 'panel-body'})
                descriptor_block = descriptor_block.find('dl', {'class' : 'NMetadata'})
                
                group_labels = []
                descriptors = []

                for child_node in descriptor_block.find_all('dt'):
                    group_labels.append(child_node.get_text().strip().strip(':'))
                for child_node in descriptor_block.find_all('dd'):
                    itemizer = child_node.find('ul')
                    
                    descriptors_by_group = []

                    for item in itemizer.find_all('li'):
                        descriptors_by_group.append(item.get_text().strip().replace('\n', ''))
                    
                    descriptors.append(descriptors_by_group)
                
                classification  = {}
                for i in range(len(group_labels)):
                    classification[group_labels[i]] = descriptors[i]
                
                document_data['classification'] = classification
        except:
            document_data['classification'] = None

        if 'Miscellaneous information' in block.text:

            try:
                misc_block = block.find('div', {'id' : 'PPMisc_Contents'})
                misc_block = misc_block.find('div', {'class' : 'panel-body'})
                misc_block = misc_block.find('dl', {'class' : 'NMetadata'})

                misc_info_groups = []
                misc_info_definitions = []

                for child_node in misc_block.find_all('dt'):
                    misc_info_groups.append(child_node.get_text().strip().strip(':'))
                for child_node in misc_block.find_all('dd'):
                    group_values = []
                    for child in child_node.find_all():
                        group_values.append(child.get_text().strip())
                    
                    misc_info_definitions.append(group_values)

                misc_info = {}

                for i in range(len(misc_info_groups)):
                    misc_info[misc_info_groups[i]] = misc_info_definitions[i]
                
                document_data['miscellaneousInformation'] = misc_info
            
            except:
                document_data['miscellaneousInformation'] = None


        if 'Dates' in block.find('div', {'class' : 'panel-heading'}).get_text():

            try:
                dates_block = block.find('div', { 'id' : 'PPDates_Contents'})
                dates_block = dates_block.find('div', { 'class' : 'panel-body'})
                dates_block = dates_block.find('dl', { 'class' : 'NMetadata'})

                date_description = []
                dates = []

                for child_node in dates_block.find_all('dt'):
                    date_description.append(child_node.get_text().strip().strip(':'))
                for child_node in dates_block.find_all('dd'):
                    event = child_node.get_text().replace('\n', '').split(';')
                    dates.append(event)
                
                date_events = {}

                for i in range(len(date_description)):
                    date_events[date_description[i]] = dates[i]
                
                document_data['dateEvents'] = date_events
            except:
                document_data['dateEvents'] = None

    # Full document text is inside <div id='text'> tag. We navigate into it, collect its content.

    try:
        document_text_lang = soup.find('div', {'id' : 'text'}).get_text()
        document_data['text'] = document_text_lang
    except:
        # Fulltext is probably not avaiable in that language.
        document_data['text'] = None

    return document_data

def collect_data(celex, languages=["EN"]):
    """
    Function that will extract all data about the document in given languages. 
    Document is uniquely determined by its celex number. Collected data will be stored into a
    dictionary and then into a json file named -> {celex_number_of_document}.json 

    If you want to extract the document in all of the available languages then give the argument
    `languages=None`

    Keys of a dictionary will be different parameter names. Data for each language will be saved into 
    a directory of that language. For example data in Slovenian language will be saved into `files/SI` folder.
    
    Parameters:
        celex : string
            celex number of the document
        languages : list of 2-character language identifiers
            languages in which we want to extract document data. (Give None if you want 
            to extract information from all of the available languages)
    
    Return
        None
    """

    # We prepare the working directories
    current_path = os.getcwd()
    files_directory = os.path.join(current_path, 'files')

    if languages == None:
        try:
            languages = get_available_languages(celex)
        except:
            languages = ['EN', 'SL', 'DE']

    for language in languages:
    
        try:
            # Collecting data in fixed language
            document_data = get_document_data_in_fixed_language(celex, language)

            if document_data == {}:
                # We didnt collect anything, no reason saving it.
                continue

            # We create the language folder if it is missing
            if language not in os.listdir(files_directory):
                os.mkdir(os.path.join(files_directory, language))
            
            language_directory = os.path.join(files_directory, language)
            output_filename = remove_forbidden_characters(celex) + '_' + language + '.json'
            with open(os.path.join(language_directory, output_filename), 'w') as outfile:
                json.dump(document_data, outfile, indent=2)

            print('Successfully collected document with celex number {} in {} language.'.format(celex, language))

            time.sleep(0.5)

        except Exception as e:
            print('FAIL at CELEX Number: {} - language: {}'.format(celex, language))
            print(e)

if __name__ == '__main__':

    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R0644'
    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R0196'
    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018D0051'

    language = 'EN'
    celex = '32018D0051'
    celex = '32018R0644'
    # celex = '62018CC0095'
    # celex = '62018CC0095'

    # print(get_available_languages(celex, ['EN', 'SI', 'DE']))
    collect_data(celex, languages=None)
import re

def get_value_or_none(pattern, text):
    """
    Given a regex pattern and a text, the function will return the match or None if no match will be found.

    Parameters:
        pattern : regex pattern (re.compile(...))
            pattern that we are looking for in the text
        text : string
            the text inside which we are looking for specific patterns

    Returns:
        In case a match is found, it returns it, otherwise it returns None.
    """

    temp = re.findall(pattern, text)
    if len(temp) > 0:
        return temp[0]
    else:
        return None

def get_list_or_none(pattern, text):
    """
    Similar function to get_value_or_none except in this case we want our match
    to be a list of strings instead of a single string.

    For example if our match is 'Slovenia, Croatia, Serbia' we would rather have this information split
    into a list of countries. (e.g. ['Slovenia', 'Croatia', 'Serbia'])

    This function will try to find the match and it will also split the string
    if the match is found. 

    Parameters:
        pattern : regex pattern
            pattern that we are looking for
        text : string
            the text in which we are looking for a match

    Returns
        list of strings or None if no match is found.
    """

    temp = re.findall(pattern, text)
    if len(temp) > 0:
        return temp[0].split(',')
    else:
        return None


def remove_forbidden_characters(name):
    """ 
    A function that will remove all the forbidden characters from the string. The forbidden characters are the ones
    that are not allowed to be used in the names of windows files. Those are  --> r'/*=:<>"|\'.

    Parameters:
        name : string
    
    Returns
        `name` without the forbidden characters
    """

    new_name = ""
    for znak in name:
        if znak in r'\/*?:<>"|':
            new_name += '_'
        else:
            new_name += znak
    
    return new_name
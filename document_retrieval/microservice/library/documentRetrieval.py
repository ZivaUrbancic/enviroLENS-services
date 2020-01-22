# DocumentRetrieval functions

from gensim.models import KeyedVectors
import string
import numpy as np
import collections
import math


def change_dict_structure(dict_list):
    """Takes list of dicts from db_query and changes to dict with key=id, value = text (used for metrices).
    Args:
        dict_list (list): List of dictionaries from db_query.
    Returns:
        texts (dictionary): Dictionary with document IDs as keys and document text as values.
    """
    texts = {}
    for dict in dict_list:
        doc_id = dict.get('document_id')
        text = dict.get('fulltext_cleaned')
        texts.update({doc_id: text})
    return texts


def similarity(token, token_list, wv):
    """Calculates similarity between token and list of tokens.
    Args:
        token (str): String for wich we are calculating similarity.
        token_list (list): List of tokens to which we are calculating similarity.
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        avreage_similarity (float): Number that signifes the similarity of token to token_list words.
    """

    similarity = 0
    num_of_tokens = 0
    for toks in token_list:
        # check if the token is in the vocabulary

        if toks in wv.vocab.keys():
            num_of_tokens += 1
            similarity += wv.similarity(toks, token) 
            avreage_similarity = similarity/num_of_tokens
    return avreage_similarity


def probability_multiply(probability, token_frequency, n):
    """Assigns score to document based on multiplication of probabilities. Probability is token frequency devided by length of document.
       In this metric only documents containing all query words have positive probability.
       Args:
           probability (float): Previously calculated probability.
           token_frequency (float):  Number of appearances of token in text.
           n (int): Length of text.
       Returns:
           probability_value (float): New caclculated probability.
    """
    probability_value = probability*(token_frequency/n)
    return probability_value

def probability_sum(probability, token_frequency, n):
    """Assigns score to document based on summation of probabilities.
    Args:
        probability (float): Previously calculated probability.
        token_frequency (float):  Number of appearances of token in text.
        n (int): Length of text.
    Returns:
        probability_value (float): New caclculated probability.
    """
    probability_value = probability+(token_frequency/n) 
    return probability_value

def word_value(word, alpha, original_tokens, top_expansion, wv):
    """values word based on whether is in original token set or expanded, if alpha -1 value equals to cosine similarity
    Args:
        word (string): Word or token for which we are calculating value.
        alpha (float): Number between 0 and 1. Weight that emphasizes the difference between original query words and expansions. 
                        Usually between 0.5 (all words are treated equal) and 1 (expansion words have value 0). 
                        For alpha -1 values equal to cosine similarity to query words.
        original_tokens(list): List of strings. Tokenized original query. Usually also extension (extension by summation of 2 consecutive words).
        top_expansion (list): List of expanded words. Usually candidates (kNN expansion).
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        value (float): Value of the word based on whether is in original token set or expanded set.
    """
    only_expanded = []
    for token in top_expansion:
        if token not in original_tokens:
            only_expanded.append(token)       
    sum_similarity = 0
    for exp_token in only_expanded:
            sum_similarity += similarity(exp_token, original_tokens, wv)        
    if alpha == -1:
        if word in original_tokens:
            value = 1
        else:
            value = similarity(word, original_tokens, wv)/sum_similarity
    else:
        if word in original_tokens:
            value = alpha
        else:
            value = (1-alpha)*similarity(word, original_tokens, wv)/sum_similarity
    return value

def probability_sum_weight(probability, token_frequency, n, word, alpha, original_tokens, top_expansion, wv):
    """Assigns weighted score to document based on summation of probabilities.
        Args:
        probability (float): Previously calculated probability.
        token_frequency (float):  Number of appearances of token in text.
        n (int): Length of text.
        word (string): Word or token for which we are calculating value.
        alpha (float): Number between 0 and 1. Weight that emphasizes the difference between original query words and expansions. 
                        Usually between 0.5 (all words are treated equal) and 1 (expansion words have value 0). 
                        For alpha -1 values equal to cosine similarity to query words.
        original_tokens(list): List of strings. Tokenized original query. Usually also extension (extension by summation of 2 consecutive words)
        top_expansion (list): List of expanded words. Usually candidates (kNN expansion).
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        probability_value (float): New caclculated probability.
    """
    probability_value = probability+(token_frequency/n)*word_value(word, alpha, original_tokens, top_expansion, wv)
    return probability_value

def top_positives(dictionary, n):
    """Takes dict and returns first n tuples of key,values sorted by values descending, returns only items with positive values.
    Args:
        dictionary (dict): Dictionary we want to sort by values.
        n (int): Number of returned items. If there are less than n items in dictonary or less than n items with positive values,
                 returns all items (with positive valuses) sorted.
    Returns:
        sorted_positives_top (list): List of n tuples. If there are less than n items in dictonary or less than n items with 
                                     positive values, returns all items (with positive valuses) sorted.
    """
    positives = {} 
    for k,v in dictionary.items():
        if v > 0:
            positives.update({k: v})
    sorted_positives = sorted(positives.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_positives) > n:
        sorted_positives_top = sorted_positives[0:n]
    else:
        sorted_positives_top = sorted_positives
    return sorted_positives_top

def probability_score(tokens, texts, probability_function, m, *args):
    # final function, takes also probability_function probability_sum_weight, but doesnt give final result (used in probability_score_sum_weights)
    """Assigns score to documents based on probability_function metric.
    Args:
        tokens (list): List of tokens (tokenized query). If needed also extension (extension by summation of 2 consecutive words).
        texts (dict):  Keys represent document ids, values are document text. 
        probability_function (function): Metric function that calculates document relavance. Functions: probability_multiply, probability_sum. Require only first 4 arguments.
        m (int): Number of returned tuples (positive scores), sorted by highest scores. If m=0 returns all.
        top_expansion (list): List of expanded words. Usually candidates (kNN expansion).
        alpha (float): Number between 0 and 1. Weight that emphasizes the difference between original query words and expansions. 
                       For alpha 0.5 all words have same weights (but not same values!), for alpha 1 expansion words have value 0. 
                       For alpha -1 values equal to cosine similarity to query words. 
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        document_probability (list): Tuples of document ids and scores that measure document relavance. Returns n tuples with highest score.
    """

    #args[0] == top_expansion
    #args[1] == alpha
    #args[2] == wv

    break_loop = False
    document_probability = {}
    for k, v in texts.items():
        n = len(v)
        if probability_function == probability_multiply:
            probability = 1
        else:
            probability = 0
        if probability_function == probability_sum_weight:
            if len(args) == 3:
                for i in range(len(tokens)):
                    token_frequency = v.count(tokens[i])
                    probability = probability_sum_weight(probability, token_frequency, n,tokens[i], args[1], tokens, args[0], args[2])
                document_probability.update({k: probability})
            else:
                print("Error, number of arguments does not match.")
                break_loop = True
                break 
        elif break_loop:
            break
        elif probability_function == probability_sum or probability_function == probability_multiply:
            if len(args) == 0:
                for i in range(len(tokens)):
                    token_frequency = v.count(tokens[i])
                    probability = probability_function(probability, token_frequency, n)
                document_probability.update({k: probability})
            else:
                print("Error, number of arguments does not match.")
                break_loop = True
                break 
        elif break_loop:
            break
        else:
            print("Error, metric function not defined.")
     
    if m == 0:
        return [(k, v) for k, v in document_probability.items()] 
    else:      
        document_probability = top_positives(document_probability ,m)        
        return document_probability

def probability_score_sum_weights(original_tokens, top_expansion, texts, m, alpha, wv): 
    # final fuction
    """As probability_score only weighted.
        Args:
        original_tokens(list): List of strings. Tokenized original query. Usually also extension (extension by summation of 2 consecutive words)
        top_expansion (list): List of expanded words. Usually candidates (kNN expansion).
        texts (dict):  Keys represent document ids, values are document text.
        m (int): Number of returned tuples (positive scores), sorted by highest scores. If m=0 returns all.
        alpha (float): Number between 0 and 1. Weight that emphasizes the difference between original query words and expansions. 
                       For alpha 0.5 all words have same weights (but not same values!), for alpha 1 expansion words have value 0. 
                       For alpha -1 values equal to cosine similarity to query words. 
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        document_score (list): Tuples of document ids and scores that measure document relavance. Returns n tuples with highest score.
    """
    tokens = original_tokens+top_expansion
    document_score = probability_score(tokens, texts, probability_sum_weight, m, top_expansion, alpha, wv)
    return document_score

def number_documents_tokens_appear(tokens, texts):
    """For each token in tokens counts the number of documents in which token has appeared.
        Args:
        tokens (list): List of tokens.
        texts (dict):  Keys represent document ids, values are document text.
    Returns:
        documents_per_token (list): List of numbers that count number of documnets in which certain token appears.
                                    Index of element in tokens list is the same as index in documents_per_token list for that element value.
    """
    documents_per_token = []
    for i in range(len(tokens)):
        documents_per_token.append(0)
    for text in texts.values():
        for i in range(len(tokens)):
            token = tokens[i]
            if token in text:
                documents_per_token[i] = documents_per_token[i]+1
    return documents_per_token

def tfidf_sum(probability, token_frequency, n, idf):
    """Assigns score to document based on TF-IDF metric.
    Args:
        probability (float): Previously calculated tfidf score.
        token_frequency (float):  Number of appearances of token in text.
        n (int): Length of text.
        idf (float): Idf of token.
    Returns:
        tfidf_value (float): New caclculated tfidf score.
    """

    tfidf_value = probability+((token_frequency/n)*idf)
    return tfidf_value

def tfidf_sum_weight(probability, token_frequency, n, idf, word, alpha, original_tokens, top_expansion, wv):
    """Assigns weighted score to document based on TF-IDF metric.
    Args:
        probability (float): Previously calculated tfidf score.
        token_frequency (float):  Number of appearances of token in text.
        n (int): Length of text.
        idf (float): Idf of token.
        word (string): Word or token for which we are calculating value.
        alpha (float): Number between 0 and 1. Weight that emphasizes the difference between original query words and expansions. 
                        Usually between 0.5 (all words are treated equal) and 1 (expansion words have value 0). 
                        For alpha -1 values equal to cosine similarity to query words.
        original_tokens(list): List of strings. Tokenized original query. Usually also extension (extension by summation of 2 consecutive words)
        top_expansion (list): List of expanded words. Usually candidates (kNN expansion).
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        tfidf_value (float): New caclculated tfidf score.
    """
    tfidf_value = probability+((token_frequency/n)*idf)*word_value(word, alpha, original_tokens, top_expansion, wv)
    return tfidf_value


def tfidf_score_str(tokens, texts, tfidf_function_name, number_all_texts_in_db, m=10,*args):
    # Same as tfidf_score, only takes tfidf_function name as input instead of function itself.
    """Assigns score to documents based on tfidf_function metric.
    Args:
        tokens (list): List of tokens (tokenized query). If needed also extension (extension by summation of 2 consecutive words).
        texts (dict):  Keys represent document ids, values are document text. 
        tfidf_function (string): Metric function that calculates document relavance. Functions: tfidf_sum; require only first 4 arguments, tfidf_sum_weight; require all arguments.
        number_all_texts_in_db (int): Number of all texts in corpus (database).
        m (int): Number of returned tuples (positive scores), sorted by highest scores. If m=0 returns all.
        top_expansion (list): List of expanded words. Usually candidates (kNN expansion).
        alpha (float): Number between 0 and 1. Weight that emphasizes the difference between original query words and expansions. 
                       For alpha 0.5 all words have same weights (but not same values!), for alpha 1 expansion words have value 0. 
                       For alpha -1 values equal to cosine similarity to query words. 
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        document_probability (list): Tuples of document ids and scores that measure document relavance. Returns n tuples with highest score.
        not_appear (list): List of words that did not occure in any document.
    """
    if tfidf_function_name == 'tfidf_sum':
            return tfidf_score(tokens, texts, tfidf_sum, number_all_texts_in_db, m)
    else:
        raise Exception("Error, different function name")

def tfidf_score(tokens, texts, tfidf_function, number_all_texts_in_db, m=10, *args):
    #final function
    """Assigns score to documents based on tfidf_function metric.
    Args:
        tokens (list): List of tokens (tokenized query). If needed also extension (extension by summation of 2 consecutive words).
        texts (dict):  Keys represent document ids, values are document text. 
        tfidf_function (function): Metric function that calculates document relavance. Functions: tfidf_sum; require only first 4 arguments, tfidf_sum_weight; require all arguments.
        number_all_texts_in_db (int): Number of all texts in corpus (database).
        m (int): Number of returned tuples (positive scores), sorted by highest scores. If m=0 returns all.
        top_expansion (list): List of expanded words. Usually candidates (kNN expansion).
        alpha (float): Number between 0 and 1. Weight that emphasizes the difference between original query words and expansions. 
                       For alpha 0.5 all words have same weights (but not same values!), for alpha 1 expansion words have value 0. 
                       For alpha -1 values equal to cosine similarity to query words. 
        wv (Word2VecKeyedVectors): Word embeddings.
    Returns:
        document_probability (list): Tuples of document ids and scores that measure document relavance. Returns n tuples with highest score.
        not_appear (list): List of words that did not occure in any document.
    """
    #args[0] == top_expansion
    #args[1] == alpha
    #args[2] == wv

    break_loop = False
    if len(args):
        tokens_together = tokens+args[0]
    else:
        tokens_together = tokens
    nb_docs_tokens_appeared = number_documents_tokens_appear(tokens_together, texts)
    filtered_nb_docs_tokens_appeared = [elt for elt in nb_docs_tokens_appeared if not elt == 0]
    not_appear = []
    appear = []

    for i in range(len(nb_docs_tokens_appeared)):

        if nb_docs_tokens_appeared[i] == 0:
            not_appear.append(tokens_together[i])
        else:
            appear.append(tokens_together[i])    
    l = number_all_texts_in_db

    document_probability = {}
    for k, v in texts.items():

        n = len(v)
        probability = 0
        for i in range(len(appear)):
            token_frequency = v.count(appear[i])
            idf = math.log(l/filtered_nb_docs_tokens_appeared[i])
            if tfidf_function == tfidf_sum:
                if len(args) == 0:
                    probability = tfidf_sum(probability, token_frequency, n, idf)
                else:
                    print("Error, number of arguments does not match")
                    break_loop = True
                    break 
            elif tfidf_function == tfidf_sum_weight:
                if len(args) == 3:
                    probability = tfidf_sum_weight(probability, token_frequency, n, idf,appear[i], args[1], tokens, args[0], args[2])
                else:
                    print("Error, number of arguments does not match")
                    break_loop = True

                    break 
        if break_loop:
            break
        document_probability.update({k: probability})
        
    if m == 0:
        return [(k, v) for k, v in document_probability.items()] 
    else:      
        document_probability = top_positives(document_probability,m)        

        return document_probability


from gensim.models import KeyedVectors
import numpy as np
from nltk.corpus   import stopwords
from nltk.tokenize import word_tokenize
import string

def tokenize(text, stopwords):
    """Tokenizes and removes stopwords from the document"""
    without_punctuations = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(without_punctuations)
    filtered = [w.lower() for w in tokens if not w in stopwords]
    return filtered

def extend_tokens(token_list, wv):
    """Extends token list summing vector pairs"""
    tokens = []
    for token in token_list:
        # check if the token is in the vocabulary
        if token in wv.vocab.keys():
            tokens.append(token)
    extention = set()
    for i in range(len(tokens)-1):
        new_token = wv.most_similar(positive=[tokens[i], tokens[i+1]])[0][0]
        extention.add(new_token)
    extention = list(extention)
    return extention

def candidate_expansion_terms(tokens, k, wv):
    """Gets the candidate expansion terms"""
    candidates = set()
    for token in tokens:
        # check if the token is in the vocabulary
        if token in wv.vocab.keys():
            result = wv.similar_by_word(token)
            limit = k if len(result) > k else len(result)
            # iterate through the most similar words
            for i in range(limit):
                candidates.add(result[i][0])
    # return list of candidates
    candidates = list(candidates)
    return candidates

def similarity(token, token_list, wv ):
    """calculates the similarity between word and list of words"""
    # calculate the similarity of the token to all tokens
    similarity = 0
    num_of_tokens = 0
    for toks in token_list:
        # check if the token is in the vocabulary
        if toks in wv.vocab.keys():
            num_of_tokens += 1
            similarity += wv.similarity(toks, token)
    return similarity/num_of_tokens

def get_similarity_pairs(tokens, candidates, wv):
    """Gets the actual expansion terms"""
    similarity_pairs = []
    for candidate in candidates:
        sim = similarity(candidate, tokens, wv)
        similarity_pairs.append((candidate, sim))
    # return the list of expansion terms with their similarities
    return similarity_pairs

def pre_retrieval_KNN(query, k, wv, n, stop_words,extension=False):
    """Find the most similar tokens(candidates) to the given query, optional:query can be extended, then the candidates are found for extended query"""
    tokens = tokenize(query, stop_words)
    if extension:
        extended = extend_tokens(tokens,wv)
        candidates = candidate_expansion_terms(tokens+extended, k, wv)
        candidates_sim = get_similarity_pairs(tokens+extended, candidates, wv)
    else:
        candidates = candidate_expansion_terms(tokens, k, wv)
        candidates_sim = get_similarity_pairs(tokens, candidates, wv)
    def takeSecond(elem):
        return elem[1]
    sort = sorted(candidates_sim, key=takeSecond)[::-1]
    sort = sort[:n]
    candidate_list = []
    for tupl in sort:
        candidate_list.append(tupl[0])
    return candidate_list
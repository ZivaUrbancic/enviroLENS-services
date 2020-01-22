import string
from gensim.models import KeyedVectors, FastText
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(word):
    # code from https://www.machinelearningplus.com/nlp/lemmatization-examples-python/
    """Map POS tag to first character lemmatize() accepts.
    Args:
        word(str): Word we wish to tag.
    Returns:
        wnl_tag(str): Tag acceptable by wordnet lemmatizer."""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    wnl_tag = tag_dict.get(tag, wordnet.NOUN)
    return wnl_tag


def tokenized_query(text, stopwords):
    """Tokenizes, lowers words and removes stopwords from the document.
        Args:
            text (str): Text we want to tokenize.
            stopwords (list): List of words we want to remove from the tokenized text.
        Returns:
            filtered_tokens (list): List of low case tokens wich does not contain stop words.
        """
    without_punctuations = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(without_punctuations)
    filtered = [lemmatizer.lemmatize(w.lower(), get_wordnet_pos(w.lower())) for w in tokens if not w in stopwords]
    return filtered


def extend_tokens(token_list, model, model_format):
    """Extends token list by summing consecutive vector pairs.
        Args:
            token_list (list): List of tokens we want to extend.
        Returns:
            extension (list): List of extensions.
            wv (Word2VecKeyedVectors): Word embeddings.
        """
    tokens = []
    if model_format == 'word2vec':
        for token in token_list:
            # check if the token is in the vocabulary
            if token in model.vocab.keys():
                tokens.append(token)
    if model_format == 'fasttext':
        for token in token_list:
            # check if the token is in the vocabulary
            if token in model.wv.vocab:
                tokens.append(token)
    extention = set()
    for i in range(len(tokens)-1):
        new_token = model.most_similar(positive=[tokens[i], tokens[i+1]])[0][0]
        extention.add(new_token)
    extention = list(extention)
    return extention


def candidate_expansion_terms(tokens, k, model, model_format):
    """Gets the candidates for expansion based on kNN.
        Args:
            tokens (list): List of tokens we want to expand.
            k (int): Number of nearest neighbours.
            wv (Word2VecKeyedVectors): Word embeddings.
        Returns:
            candidates (list): List of candidates.
    """
    candidates = set()
    if model_format == 'word2vec':
        for token in tokens:
            # check if the token is in the vocabulary
            if token in model.vocab.keys():
                result = model.similar_by_word(token)
                limit = k if len(result) > k else len(result)
                # iterate through the most similar words
                for i in range(limit):
                    candidates.add(result[i][0])
    elif model_format == 'fasttext':
        for token in tokens:
            # check if the token is in the vocabulary
            if token in model.wv.vocab:
                result = model.most_similar(token)
                limit = k if len(result) > k else len(result)
                # iterate through the most similar words
                for i in range(limit):
                    candidates.add(result[i][0])
    else:
        raise Exception('Model type incorrect')
    # return list of candidates
    candidates = list(candidates)
    return candidates


def similarity(token, token_list, model, model_format ):
    """Calculates the similarity between token and list of tokens.
        Args:
            token (str): String for wich we are calculating similarity.
            token_list (list): List of tokens to wich we are calculating similarity of token.
            wv (Word2VecKeyedVectors): Word embeddings.
        Returns:
            avreage_similarity (float): Number that signifes the similarity of token to token list words.
        """
    # calculate the similarity of the token to all tokens
    similarity = 0
    num_of_tokens = 0
    if model_format == 'word2vec':
        for tokens in token_list:
            # check if the token is in the vocabulary
            if tokens in model.vocab.keys():
                num_of_tokens += 1
                similarity += model.similarity(tokens, token)
    elif model_format == 'fasttext':
        for tokens in token_list:
            # check if the token is in the vocabulary
            if tokens in model.wv.vocab:
                num_of_tokens += 1
                similarity += model.similarity(tokens, token)
    else:
        raise Exception('Model type incorrect')
    return similarity/num_of_tokens


def get_similarity_pairs(tokens, candidates, wv, model_format):
    """Calculates similarity to tokens for list of candidates.
        Args:
            tokens (list): List of tokens to wich similarity is calculated
            candidates (list): List of tokens for wich similarity is calculated.
            wv (Word2VecKeyedVectors): Word embeddings.
        Returns:
            similarity_pairs (list): List of tuples. Tuples are pairs of candidates and their similarity to tokens.
        """
    similarity_pairs = []
    for candidate in candidates:
        sim = similarity(candidate, tokens, wv, model_format)
        similarity_pairs.append((candidate, sim))
    # return the list of expansion terms with their similarities
    return similarity_pairs


def pre_retrieval_KNN(query, k, wv, n, stop_words, model_format, extension=False):
    """Find n most similar tokens(candidates) to the given query, optional:
        query can be extended, then the candidates are found for extended query.
        Args:
            query (string): User query we want to expand.
            k (int): Number of nearest neighbours.
            wv (Word2VecKeyedVectors): Word embeddings.
            n (int): Number of candidates (with the highest simiarity) that is returned.
            stopwords (list): List of words we want to remove from the tokenized text.
        Returns:
            candidate_list (list): List of n candidates with the highest similarity to query tokens.
        """
    tokens = tokenized_query(query, stop_words)
    if extension:
        extended = extend_tokens(tokens, wv, model_format)
        candidates = candidate_expansion_terms(tokens+extended, k, wv, model_format)
        candidates_sim = get_similarity_pairs(tokens+extended, candidates, wv, model_format)
    else:
        candidates = candidate_expansion_terms(tokens, k, wv, model_format)
        candidates_sim = get_similarity_pairs(tokens, candidates, wv, model_format)
    def takeSecond(elem):
        return elem[1]
    sort = sorted(candidates_sim, key=takeSecond)[::-1]
    candidate_list = []
    for tupl in sort:
        candidate_list.append(tupl[0])
    cleaned = [word for word in candidate_list if word.isalpha()]
    lemmatized = [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in cleaned]
    candidate_list = [w for w in lemmatized if w not in tokens]
    candidate_list = candidate_list[:n]
    return candidate_list

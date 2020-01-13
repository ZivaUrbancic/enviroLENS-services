import numpy as np
import matplotlib.pyplot as plt


class DocumentSimilarity:
    """
    Given a document embedding, provides tools for analysis of document similarity.

    Args:
        embedding (numpy.ndarray): matrix of document embeddings
        indices (list(int)): stores document ids in the original database for the documents with embeddings in
            'embedding'.

    Methods:
        get_embedding(): Retrieves the embedding from attribute '__embedding'.
        get_indices(): Retrieves the embedding from attribute '__indices'.
        euclid_similarity(emb1, emb2): Calculate the Euclid similarity between two embeddings.
        cosine_similarity(emb1, emb2): Calculate the cosine similarity between two embeddings.
        k_nearest_neighbors(index, k=10, similarity=self.euclid_similarity): Get the k documents with embeddings nearest
            to the document embedding we chose.
    """

    def __init__(self, embedding, indices):
        """
        Args:
            embedding (numpy.ndarray): matrix of document embeddings
            indices (list(int)): list of document ids in the original database for the documents with embeddings in
                'embedding'.
        """

        self.__embedding = embedding
        self.__indices = indices

    def get_embedding(self):
        """
        Retrieves the embedding.

        Returns:
            obj: The embedding stored in the instance
        """

        return self.__embedding

    def get_indices(self):
        """
        Retrieves the indices.

        Returns:
            obj: The indices stored in the instance
        """

        return self.__indices

    def euclid_similarity(self, emb1, emb2):
        """
        Calculates the Euclid similarity between two embeddings.

        Args:
            emb1 (numpy.ndarray): the first embedding we want to compare
            emb2 (numpy.ndarray): the second embedding we want to compare

        Returns:
            numpy.float32: Euclid distance between given embeddings
        """

        return np.linalg.norm(emb1 - emb2)

    def cosine_similarity(self, emb1, emb2):
        """
        Calculates cosine similarity between two embeddings.

        Args:
            emb1 (numpy.ndarray): the first embedding we want to compare
            emb2 (numpy.ndarray): the second embedding we want to compare

        Returns:
            numpy.float32: cosine similarity between given embeddings
        """

        dot = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        return dot / (norm1 * norm2)

    def k_nearest_neighbors(self, emb, k=10, similarity=None):
        """
        Get the k documents with embeddings nearest to the document embedding we chose.

        Args:
            emb (numpy.ndarray): embedding of the chosen document, whose neighbors we are trying to find
            k (int): number of neighbors we want to find. (Default = 10)
            similarity (function): metric function that we want to use for computing the distance between documents
                (Default = self.euclid_similarity)

        Returns:
            list: a list of k indices of the k documents whose embeddings are closest to the chosen embedding in the
            specified metric
        """

        # Set 'similarity' to self.euclid_similarity if nothing is set.
        if similarity is None:
            similarity = self.euclid_similarity

        # calculate the similarities and revert it
        sims = [similarity(emb, d) for d in self.__embedding]

        # sort and get the corresponding indices
        indices = []
        for c, i in enumerate(np.argsort(sims)):
            if c == k:
                break
            indices.append(i)

        # return indices of the neighbors
        return indices

    def compute_similarities(self, ind, emb):
        """Computes similarities between a given document and all the documents with their embeddings in parameter
        '__embedding'.

        Args:
            ind (int): the index of the given document in the original database.
            emb (numpy.ndarray): embedding of the source document.

        Returns:
            numpy.ndarray: matrix with three columns: id of document number one, id of document number two and
                similarity between them.
        """

        if len(self.__embedding) > 0:
            similarities = np.matmul(self.__embedding, emb)
            res = [[self.__indices[i], ind, similarities[i]] for i in range(len(self.__indices))] + \
                  [[ind, self.__indices[i], similarities[i]] for i in range(len(self.__indices))]
        else:
            res = []
        return res

    def new_document(self, ind, emb):
        """
        Adds the embedding of a new document to the '__embedding', its index to the '__indices' and returns its
        similarities with all the embeddings that are already in the '__embeddings'.

        Args:
            ind (int): index of the document we are adding
            emb (numpy.ndarray): the embedding of the new document

        Returns:
            numpy.ndarray: matrix with three columns: id of document number one, id of document number two and
                similarity between them.
        """

        similarities = self.compute_similarities(ind, emb)
        if len(self.__embedding) == 0:
            self.__embedding = [emb]
        else:
            self.__embedding = np.vstack([self.__embedding, emb])
        self.__indices = self.__indices.append(ind)
        return similarities

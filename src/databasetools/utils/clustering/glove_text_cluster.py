"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      glove_text_cluster.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/07/2024 07:57:31
Modified By: Mathew Cosgrove
-----
"""

import numpy as np
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from nltk.tokenize import word_tokenize

# word2vec_output_file = 'glove.6B.100d.txt.word2vec'
from .text_cluster import TextClusterer


class GloveKMeansClusterer(TextClusterer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path = kwargs.get("file_path")
        word2vec_output_file = "glove.6B.100d.txt.word2vec"
        glove2word2vec(self.file_path, word2vec_output_file)
        self.glove_model = KeyedVectors.load_word2vec_format(word2vec_output_file, binary=False)

    def preprocess_titles(self):
        self.lemmatize_titles()
        return [word_tokenize(title) for title in self.titles]

    def vectorize_titles(self) -> np.array:
        """Vectorize titles using GloVe word embeddings. This method averages the word vectors in each title.

        Returns:
        - np.array: A 2D numpy array of shape (n_titles, n_features) where n_titles is the number of titles and n_features is the number of features in the GloVe word embeddings.

        """
        vectors = []
        for words in self.preprocess_titles():
            word_vectors = [self.glove_model[word] for word in words if word in self.glove_model and word.isalpha()]
            if word_vectors:
                vectors.append(np.mean(word_vectors, axis=0))
            else:
                vectors.append(np.zeros(self.glove_model.vector_size))
        return np.array(vectors)

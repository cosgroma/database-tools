"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      tfid_text_cluster.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/07/2024 07:57:01
Modified By: Mathew Cosgrove
-----
"""

from typing import Any
from typing import Dict

from sklearn.feature_extraction.text import TfidfVectorizer

from .text_cluster import TextClusterer


class TfidfKMeansClusterer(TextClusterer):
    def __init__(self, **kwargs: Dict[str, Any]):
        super().__init__(**kwargs)
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def preprocess_titles(self):
        if not self.titles:
            print("No titles to preprocess")
            return []

        return self.lemmatize_titles()

    def vectorize_titles(self):
        preprocessed_titles = self.preprocess_titles()
        return self.vectorizer.fit_transform(preprocessed_titles)

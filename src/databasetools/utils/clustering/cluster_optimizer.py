"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      cluster_optimizer.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/10/2024 07:35:52
Modified By: Mathew Cosgrove
-----
"""

from typing import Dict

import numpy as np
from sklearn.metrics import silhouette_score

from .text_cluster import TextClusterer


class ClusteringEvaluator:
    """A class to evaluate clustering performance using various metrics.

    Attributes:
    - vectorized_data (np.ndarray): The array of vectorized titles, where each row corresponds to a text item.
    - labels (np.ndarray): The array of cluster labels assigned to each title.

    Methods:
    - evaluate_silhouette_score: Calculate the silhouette score for the current clustering.
    - evaluate_davies_bouldin_score: Calculate the Davies-Bouldin score for the current clustering.
    - evaluate_inertia: Calculate the inertia of the model used for clustering.
    - get_evaluation_summary: Generates a summary of all evaluation metrics.

    """

    def __init__(self, vectorized_data: np.ndarray, labels: np.ndarray):
        """
        Initialize the evaluator with the data used for clustering and the labels produced by a clustering algorithm.

        Args:
        - vectorized_data (np.ndarray): The array of vectorized titles, where each row corresponds to a text item.
        - labels (np.ndarray): The array of cluster labels assigned to each title.
        """
        self.vectorized_data = vectorized_data
        self.labels = labels

    def evaluate_silhouette_score(self) -> float:
        """
        Calculate the silhouette score for the current clustering.

        Returns:
        float: The silhouette score.
        """
        if np.unique(self.labels).size == 1:
            raise ValueError("Cannot compute silhouette score with only one cluster.")
        return silhouette_score(self.vectorized_data, self.labels)

    def evaluate_davies_bouldin_score(self) -> float:
        """
        Calculate the Davies-Bouldin score for the current clustering.

        Returns:
        float: The Davies-Bouldin score, lower is better.
        """
        return 0.0  # davies_bouldin_score(self.vectorized_data, self.labels)

    def evaluate_inertia(self, model) -> float:
        """
        Calculate the inertia of the model used for clustering.

        Args:
        model (KMeans): The clustering model which must have an 'inertia_' attribute.

        Returns:
        float: The inertia value.
        """
        return model.inertia_

    def get_evaluation_summary(self, model) -> Dict[str, float]:
        """
        Generates a summary of all evaluation metrics.

        Args:
        model (KMeans): The clustering model.

        Returns:
        Dict[str, float]: A dictionary containing all the computed metrics.
        """
        summary = {
            "Silhouette Score": self.evaluate_silhouette_score(),
            "Davies-Bouldin Score": self.evaluate_davies_bouldin_score(),
            "Inertia": self.evaluate_inertia(model),
        }
        return summary


class ClusterOptimizer:
    def __init__(self, clusterer: TextClusterer, max_clusters: int = 10):
        self.clusterer = clusterer
        self.max_clusters = max_clusters

        self.scores = {"silhouette": {}, "inertia": {}}
        self.eval_scores = {}

    def get_scores(self) -> Dict[str, Dict[int, float]]:
        return self.scores

    def get_eval_scores(self) -> Dict[int, Dict[str, float]]:
        return self.eval_scores

    def run_cluster_eval(self, num_clusters: int):
        model, vectors, labels = self.clusterer.perform_clustering(num_clusters=num_clusters)

        self.labels = labels
        self.data = vectors

        self.eval = ClusteringEvaluator(self.data, self.labels)

        model.fit(self.data)
        self.scores["inertia"][num_clusters] = self.eval.evaluate_inertia(model)
        self.scores["silhouette"][num_clusters] = self.eval.evaluate_silhouette_score()

        self.eval_scores[num_clusters] = self.eval.get_evaluation_summary(model)

        return self.eval_scores[num_clusters]

    def best_silhouette(self):
        silhouette_scores = self.scores["silhouette"]
        return min(silhouette_scores, key=silhouette_scores.get)

    def asses_elbow_index(self):
        inertias = self.scores["inertia"]
        # inertia_keys = list(inertias.keys())
        inertia_values = list(inertias.values())
        elbow_index = 0
        for i in range(1, len(inertia_values) - 1):
            if inertia_values[i] - inertia_values[i + 1] < 0.1:
                elbow_index = i
                break
        return elbow_index

    def run_optimization(self):
        for k in range(2, self.max_clusters + 1):
            self.run_cluster_eval(k)
        elbow_index = self.asses_elbow_index()
        best_silhouette = self.best_silhouette()
        return best_silhouette, elbow_index

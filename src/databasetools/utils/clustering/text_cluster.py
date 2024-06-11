import json
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
from sklearn.cluster import KMeans


class TextClusterer(ABC):
    def __init__(self, **kwargs: dict):
        self.titles = []
        self.cluster_labels = None

    def set_titles(self, titles: List[str]):
        self.titles = titles

    def load_titles(self, file_path: str, bad_title_list: Optional[List[str]] = None) -> List[str]:
        if bad_title_list is None:
            bad_title_list = [""]

        with Path.open(file_path) as f:
            titled_items = json.load(f)
        return self.load_titles_from_dict(titled_items, bad_title_list)

    def load_titles_from_dict(self, titled_items: Dict[str, Any], bad_title_list: Optional[List[str]] = None) -> List[str]:
        if bad_title_list is None:
            bad_title_list = [""]
        titles = [item["title"] for item in titled_items.values() if item["title"] is not None]
        self.titles = titles
        for bad_title in bad_title_list:
            while bad_title in titles:
                titles.remove(bad_title)
        return titles

    def lemmatize_titles(self):
        self.titles = [title.lower().strip() for title in self.titles]
        return self.titles

    @abstractmethod
    def preprocess_titles(self): ...

    @abstractmethod
    def vectorize_titles(self): ...

    def perform_clustering(self, num_clusters: int = 3) -> Tuple[KMeans, np.array, np.array]:
        self.vectors = self.vectorize_titles()
        self.model = KMeans(n_clusters=num_clusters, random_state=42)
        self.cluster_labels = self.model.fit_predict(self.vectors)
        return self.model, self.vectors, self.cluster_labels

    def get_clusters(self) -> Dict[int, List[str]]:
        if self.cluster_labels is None:
            raise ValueError("Clustering has not been performed yet.")
        clusters = {str(i): [] for i in np.unique(self.cluster_labels)}
        for title, label in zip(self.titles, self.cluster_labels):
            clusters[str(label)].append(title)
        return clusters

    def show_clusters(self, show_titles: bool = False):
        clusters = self.get_clusters()
        for label, titles in clusters.items():
            print(f"Cluster {label}: {len(titles)} titles")
            if show_titles:
                print("\n-----------\n")
                for idx, title in enumerate(titles):
                    print(f"{idx+1}. {title}")
                print("\n-----------\n")

"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      nlp_manager.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/10/2024 07:41:06
Modified By: Mathew Cosgrove
-----
"""

import json
import os
import sys
from pathlib import Path
from typing import List
from typing import Optional

# Plotting
import matplotlib.pyplot as plt

from databasetools.utils.clustering.cluster_optimizer import ClusterOptimizer

# from databasetools.utils.clustering.bert_text_cluster import BertKMeansClusterer
from databasetools.utils.clustering.glove_text_cluster import GloveKMeansClusterer
from databasetools.utils.clustering.tfid_text_cluster import TextClusterer
from databasetools.utils.clustering.tfid_text_cluster import TfidfKMeansClusterer

if os.name == "nt":
    models_volume = Path("F:\\")
    env = "Windows"
else:
    models_volume = Path("/mnt/f")
    env = "Linux"

models_dir = models_volume / "models"

glove_file = "glove.6B.50d.txt"
glove_path = models_dir / "nlp" / "glove" / glove_file

cluster_algroithm_map = {
    "tfidf": {
        "class": TfidfKMeansClusterer,
        "options": {},
    },
    "glove": {
        "class": GloveKMeansClusterer,
        "options": {"file_path": glove_path},
    },
    # "bert": {
    #     "class": BertKMeansClusterer,
    #     "options": {
    #     },
    # }
}


def run_clusterer(clusterer_class: TextClusterer, options, text_data: str, num_clusters: int = 3) -> dict:
    clusterer: TextClusterer = clusterer_class(**options)
    clusterer.load_titles(text_data)
    model, vectors, labels = clusterer.perform_clustering(num_clusters=num_clusters)
    return clusterer.get_clusters()


def run_all_cluster_algorithms(title_items_json: str, num_clusters: int = 3):
    # results = {}
    with Path.open(title_items_json) as f:
        titled_items = json.load(f)

    for cluster_algorithm, cluster_options in cluster_algroithm_map.items():

        clusterer: TextClusterer = cluster_options["class"](**cluster_options["options"])
        clusterer.load_titles_from_dict(titled_items, bad_title_list=bad_title_list)
        model, vectors, labels = clusterer.perform_clustering(num_clusters=num_clusters)
        clusters = clusterer.get_clusters()
        cluster_output_file = f"{cluster_algorithm}_clusters_{num_clusters}.json"
        with Path.open(cluster_output_file, "w") as f:
            metadata = {
                "cluster_algorithm": cluster_algorithm,
                "num_clusters": num_clusters,
                "title_items_json": title_items_json,
            }
            data_package = {
                "metadata": metadata,
                "clusters": clusters,
            }
            json.dump(data_package, f, indent=4)


def run_optimize_cluster_algorithms(title_items_json: str, max_clusters: int = 15, bad_title_list: Optional[List[str]] = None):
    with Path.open(title_items_json) as f:
        titled_items = json.load(f)

    results = {}
    results_output_file = f"clustering_optimization_limit_{max_clusters}.json"
    for cluster_algorithm, cluster_options in cluster_algroithm_map.items():
        clusterer: TextClusterer = cluster_options["class"](**cluster_options["options"])
        clusterer.load_titles_from_dict(titled_items, bad_title_list=bad_title_list)

        optimizer = ClusterOptimizer(clusterer, max_clusters=max_clusters)
        best_silhouette, elbow_index = optimizer.run_optimization()

        print(f"Optimal number of clusters by Silhouette Score for {cluster_algorithm}:", best_silhouette)
        print(f"Elbow Index for {cluster_algorithm}:", elbow_index)
        results[cluster_algorithm] = {
            "best_silhouette": best_silhouette,
            "elbow_index": elbow_index,
            "scores": optimizer.get_scores(),
            "eval_scores": optimizer.get_eval_scores(),
        }
    with Path.open(results_output_file, "w") as f:
        json.dump(results, f, indent=4)

    fig, ax = plt.subplots(len(results.items()), 1, figsize=(12, 12))
    ax_count = 0
    for cluster_algorithm, cluster_results in results.items():
        scores = cluster_results["scores"]
        silhouette_scores = scores["silhouette"]
        inertia_scores = scores["inertia"]
        # eval_scores = cluster_results["eval_scores"]
        silhouette_keys = list(silhouette_scores.keys())
        silhouette_values = list(silhouette_scores.values())
        inertia_keys = list(inertia_scores.keys())
        inertia_values = list(inertia_scores.values())
        # eval_keys = list(eval_scores.keys())
        # eval_values = list(eval_scores.values())
        ax0_1 = ax[ax_count].twinx()

        ax[ax_count].plot(silhouette_keys, silhouette_values, "g-", label="Silhouette Score")
        ax0_1.plot(inertia_keys, inertia_values, "b-", label="Inertia")
        ax[ax_count].set_title(f"{cluster_algorithm} Clustering Scores")
        ax[ax_count].set_xlabel("Number of Clusters")
        ax[ax_count].set_ylabel("Silhouette Score")
        ax0_1.set_ylabel("Inertia")
        ax[ax_count].legend()
        ax[ax_count].grid()
        ax_count += 1
    plt.tight_layout()
    plt.savefig(f"clustering_scores_{max_clusters}.png")
    plt.close()
    return results


if __name__ == "__main__":
    title_items_json = sys.argv[1]
    max_clusters = int(sys.argv[2])
    bad_title_list = ["New chat"]
    run_optimize_cluster_algorithms(title_items_json, max_clusters, bad_title_list)
    run_all_cluster_algorithms(title_items_json, 29)
    sys.exit(0)

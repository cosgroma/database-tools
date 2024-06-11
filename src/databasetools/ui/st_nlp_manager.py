"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      st_nlp_manager.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/07/2024 10:07:34
Modified By: Mathew Cosgrove
-----
"""

import json
import os
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from databasetools.utils.glove_text_cluster import GloveKMeansClusterer
from databasetools.utils.tfid_text_cluster import TextClusterer
from databasetools.utils.tfid_text_cluster import TfidfKMeansClusterer

# Set up paths based on the operating system
if os.name == "nt":
    models_volume = Path("F:\\")
else:
    models_volume = Path("/mnt/f")

models_dir = models_volume / "models"
glove_file = "glove.6B.50d.txt"
glove_path = models_dir / "nlp" / "glove" / glove_file

# Define cluster algorithm options
cluster_algorithm_map = {
    "TF-IDF": {
        "class": TfidfKMeansClusterer,
        "options": {},
    },
    "GloVe": {
        "class": GloveKMeansClusterer,
        "options": {"file_path": glove_path},
    },
}


def run_clusterer(clusterer_class: TextClusterer, options, json_data: Dict[str, Dict], num_clusters: int = 3) -> dict:
    clusterer: TextClusterer = clusterer_class(**options)
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    clusterer.load_titles_from_dict(json_data)
    clusterer.perform_clustering(num_clusters=num_clusters)
    return clusterer.get_clusters()


def plot_clusters_bar(clusters: dict):
    hist_bin_values = [(len(cluster),) for cluster in clusters.values()]
    chart_data = pd.DataFrame(hist_bin_values, columns=["count"])
    st.bar_chart(chart_data, use_container_width=True)
    # alt.Chart(chart_data).mark_bar().encode(
    #     x='count:Q',
    #     y="cluster:O"
    # ).properties(height=700)


# def plot_horizontal_bar_chart(cluster: dict):
#     hist_bin_values = [(len(cluster),) for cluster in cluster.values()]
#     chart_data = pd.DataFrame(hist_bin_values, columns=["Number of Titles"])
#     st.bar_chart(chart_data, use_container_width=True)


def show_cluster_list(clusters: dict):
    for cluster_id, titles in clusters.items():
        st.write(f"Cluster {cluster_id}:")
        for title in titles:
            st.write(f"- {title}")


def get_cluster_ids(clusters: dict):
    return list(clusters.keys())


def make_dropdown_options(cluster_ids: list):
    return {str(cluster_id): cluster_id for cluster_id in cluster_ids}


def show_cluster_titles(clusters: dict, cluster_id: int):
    st.write(f"Cluster {cluster_id}:")
    for title in clusters[cluster_id]:
        st.write(f"- {title}")


def main_v0():
    st.title("Text Clustering Application")

    if "json_data" not in st.session_state:
        st.session_state.json_data = {}  # Initialize empty state if nothing uploaded yet

    if "clusters" not in st.session_state:
        st.session_state.clusters = {}

    algorithm = st.selectbox("Choose the clustering algorithm:", list(cluster_algorithm_map.keys()))
    num_clusters = st.number_input("Number of Clusters", min_value=2, value=3, step=1)
    uploaded_file = st.file_uploader("Upload JSON file", type=["json"])

    if st.button("Cluster Texts") and st.session_state.json_data:
        clusters = run_clusterer(
            cluster_algorithm_map[algorithm]["class"], cluster_algorithm_map[algorithm]["options"], st.session_state.json_data, num_clusters
        )
        st.session_state.clusters = clusters
        st.success("Texts clustered successfully!")

    elif "json_data" in st.session_state and not st.session_state.json_data:
        st.warning("Please upload a JSON file.")

    if st.session_state.clusters:
        st.write("Clustered Titles:")

        plot_clusters_bar(st.session_state.clusters)
        cluster_ids = get_cluster_ids(st.session_state.clusters)
        cluster_dropdown = st.selectbox("Select a cluster to view titles:", make_dropdown_options(cluster_ids))
        show_cluster_titles(st.session_state.clusters, int(cluster_dropdown))

    if uploaded_file is not None:
        # Read file and store it in the session state
        json_data = json.load(uploaded_file)
        st.session_state.json_data = json_data


def main():
    st.title("Text Clustering Application")

    if "json_data" not in st.session_state:
        st.session_state.json_data = {}  # Initialize empty state if nothing uploaded yet

    if "clusters" not in st.session_state:
        st.session_state.clusters = {}

    algorithm = st.selectbox("Choose the clustering algorithm:", list(cluster_algorithm_map.keys()))
    num_clusters = st.number_input("Number of Clusters", min_value=2, value=3, step=1)
    uploaded_file = st.file_uploader("Upload JSON file", type=["json"])

    if st.button("Cluster Texts") and st.session_state.json_data:
        clusters = run_clusterer(
            cluster_algorithm_map[algorithm]["class"], cluster_algorithm_map[algorithm]["options"], st.session_state.json_data, num_clusters
        )
        st.session_state.clusters = clusters
        st.success("Texts clustered successfully!")

    elif "json_data" in st.session_state and not st.session_state.json_data:
        st.warning("Please upload a JSON file.")

    if st.session_state.clusters:
        col1, col2 = st.columns(2)

        with col1:
            st.write("Clustered Titles:")
            plot_clusters_bar(st.session_state.clusters)

        with col2:
            cluster_ids = get_cluster_ids(st.session_state.clusters)
            cluster_dropdown = st.selectbox("Select a cluster to view titles:", make_dropdown_options(cluster_ids))
            show_cluster_titles(st.session_state.clusters, int(cluster_dropdown))

    if uploaded_file is not None:
        # Read file and store it in the session state
        json_data = json.load(uploaded_file)
        st.session_state.json_data = json_data


if __name__ == "__main__":
    main()

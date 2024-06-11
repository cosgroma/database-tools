"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      bert_text_cluster.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/07/2024 07:54:50
Modified By: Mathew Cosgrove
-----
"""

import torch
from transformers import BertModel
from transformers import BertTokenizer

from .text_cluster import TextClusterer


class BertKMeansClusterer(TextClusterer):
    def __init__(self, titles, model_name="bert-base-uncased"):
        super().__init__(titles)
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()  # Set the model to evaluation mode

    def preprocess_titles(self):
        super().preprocess_titles()
        # Tokenize titles; this method could be modified to handle larger texts appropriately
        return [self.tokenizer(title, padding="max_length", max_length=512, truncation=True, return_tensors="pt") for title in self.titles]

    def vectorize_titles(self):
        # Use BERT to get embeddings; using the mean of the last hidden state as the sentence embedding
        vectors = []
        with torch.no_grad():  # Disable gradient calculation for inference
            for processed_title in self.preprocess_titles():
                output = self.model(**processed_title)
                # Get the mean of the embeddings from the last hidden layer
                mean_embedding = output.last_hidden_state.mean(dim=1).squeeze().numpy()
                vectors.append(mean_embedding)
        return vectors

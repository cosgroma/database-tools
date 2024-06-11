"""
@brief
@details
@author    Mathew Cosgrove
@date      Monday June 10th 2024
@file      local_ai_testing.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/10/2024 02:05:16
Modified By: Mathew Cosgrove
-----
"""

# Make sure to `pip install openai` first
from openai import OpenAI

client = OpenAI(base_url="http://sergeant.work:1234/v1", api_key="lm-studio")


def get_embedding(text, model="nomic-ai/nomic-embed-text-v1.5-GGUF"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def get_chat(chat_model: str):
    completion = client.chat.completions.create(
        model=chat_model,
        messages=[{"role": "system", "content": "Always answer in rhymes."}, {"role": "user", "content": "Introduce yourself."}],
        temperature=0.7,
    )

    print(completion.choices[0].message)


CHAT_MODEL = "QuantFactory/deepseek-math-7b-instruct-GGUF"
# print(get_embedding("Once upon a time, there was a cat."))
get_chat(CHAT_MODEL)

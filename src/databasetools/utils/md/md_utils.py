"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      md_utils.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/13/2024 12:44:35
Modified By: Mathew Cosgrove
-----
"""

import json
import os
import re
import uuid
from collections import Counter
from pathlib import Path
from typing import List
from typing import Optional

import markdown
import mistune


def get_numbered_list(lst) -> List[str]:
    tmp = [f"{i+1}. {item}" for i, item in enumerate(lst)]
    return "\n".join(tmp)


# pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
# language_match = r'^```(\w+)\s*\n'
# code_blocks = re.findall(pattern, string, re.DOTALL | re.MULTILINE)
# languages = re.findall(language_match, string, re.DOTALL | re.MULTILINE)
# print(*[r for r in code_blocks], sep='\n')
# print(languages)
# zip_code = zip(code_blocks, languages)


def get_code_blocks(markdown_string) -> List[str]:
    pattern = r"^```(?:\w+)?\s*\n(.*?)(?=^```)```"
    language_match = r"^```(\w+)\s*\n"
    # title_string = r"^#+\s*(.*)"
    # source_file_regex = r'^\s*source_file:\s*(.*)'
    code_blocks = re.findall(pattern, markdown_string, re.DOTALL | re.MULTILINE)
    languages = re.findall(language_match, markdown_string, re.DOTALL | re.MULTILINE)

    if len(code_blocks) > len(languages):
        for _ in range(len(code_blocks) - len(languages)):
            languages.append("")
    return zip(code_blocks, languages)


def markdown_has_code_blocks(markdown_string):
    pattern = r"^```(?:\w+)?\s*\n(.*?)(?=^```)```"
    return re.search(pattern, markdown_string, re.DOTALL | re.MULTILINE) is not None


def extract_markdown_table_v1(markdown_table):
    """Extracts the data from a markdown table.

    Args:
      markdown_table: A string containing the markdown table.

    Returns:
      A list of dictionaries, where each dictionary represents a row in the table.
    """

    # Compile the regular expression.
    regex = re.compile(r"\|(.*?)\|.*?\|.*?\|")

    # Extract the data from the markdown table.
    data = []
    for match in regex.finditer(markdown_table):
        row = {}
        columns = match.group(1).split("|")
        for i in range(len(columns) - 1):
            row[columns[i].strip()] = columns[i + 1].strip()
        data.append(row)

    return data


def extract_markdown_table_v2(markdown_table):
    """Extracts the data from a markdown table.

    Args:
      markdown_table: A string containing the markdown table.

    Returns:
      A list of dictionaries, where each dictionary represents a row in the table.
    """

    # Parse the markdown table.
    parsed_markdown = markdown.markdown(markdown_table, extensions=["markdown.extensions.tables"])
    # print(parsed_markdown)
    # Extract the data from the parsed markdown
    data = []
    for row in parsed_markdown.table:
        row_data = {}
        for column in row.cells:
            row_data[column.header] = column.text
        data.append(row_data)

    return data


# def extract_markdown_table(md_table):
#     # Regex patterns
#     row_pattern = r"^\|(.+?)\|$"
#     cell_pattern = r"\s*\|\s*"

#     # Find all rows in the table
#     rows = re.findall(row_pattern, md_table, re.MULTILINE)

#     # Parse each row
#     parsed_table = []
#     for row_idx, row in enumerate(rows):
#         cells = re.split(cell_pattern, row.strip())  # Splitting the row into cells and excluding the first and last empty strings
#         if row_idx == 0:
#             column_names = cells
#         if cells and not re.match(r"-+", cells[0]):  # Exclude the header separator row
#             parsed_table.append(cells)


class MarkdownElementExtractor(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__()
        self.elements = []

    def heading(self, text, level):
        element_id = str(uuid.uuid4())
        self.elements.append({"id": element_id, "type": "heading", "level": level, "content": text})
        return super().heading(text, level)

    def list(self, text: str, ordered: bool, **attrs):
        element_id = str(uuid.uuid4())
        list_type = "ordered" if ordered else "unordered"
        self.elements.append({"id": element_id, "type": "list", "list_type": list_type, "content": text})
        return super().list(text, ordered, **attrs)

    def table(self, header, body):
        element_id = str(uuid.uuid4())
        table_html = f"<table><thead>{header}</thead><tbody>{body}</tbody></table>"
        self.elements.append({"id": element_id, "type": "table", "content": table_html})
        return table_html

    def link(self, text: str, url: str, title=None):
        element_id = str(uuid.uuid4())
        self.elements.append({"id": element_id, "type": "link", "url": url, "title": title, "content": text})
        return super().link(text, url, title)

    def image(self, text: str, url: str, title=None):
        element_id = str(uuid.uuid4())
        self.elements.append({"id": element_id, "type": "image", "text": text, "url": url, "alt_text": title})
        return super().image(text, url, title)

    def block_code(self, code: str, info=None):
        element_id = str(uuid.uuid4())
        self.elements.append({"id": element_id, "type": "code_block", "language": info, "content": code})
        return super().block_code(code, info)


class MarkdownManager:
    """A class for managing markdown files.

    Attributes:
        directory_path (Path): The path to the directory containing the markdown files.
        elements (List[dict]): A list of dictionaries, where each dictionary represents an element in the markdown files.

    Methods:
        parse_markdown_file(file_path: Path) -> List[dict]: Parses a markdown file and extracts the elements.
        parse_markdown(markdown_text: str) -> MarkdownElementExtractor: Parses a markdown string and extracts the elements.
        extract_elements() -> List[dict]: Extracts the elements from the markdown files in the directory.
        save_to_json(json_path: Path): Saves the elements to a JSON file.
        read_markdown_files(directory: Path) -> str: Reads the markdown files in the directory and returns the text data.
        clean_text(text: str) -> str: Cleans the text data.
        word_frequency(text: str) -> Counter: Calculates the word frequency.
    """

    def __init__(self, directory_path: Optional[Path] = None):
        """Initializes the MarkdownManager.

        Args:
            directory_path (Path): The path to the directory containing the markdown files.
        """
        if directory_path is None:
            directory_path = Path.cwd()
        self.directory_path = directory_path
        self.elements = []

    def parse_markdown_file(self, file_path: Path) -> List[dict]:
        """Parses a markdown file and extracts the elements.

        Args:
            file_path (Path): The path to the markdown file.

        Returns:
            List[dict]: A list of dictionaries, where each dictionary represents an element in the markdown file.
        """
        with Path.open(file_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        renderer = MarkdownElementExtractor()
        markdown = mistune.create_markdown(renderer=renderer)
        markdown(markdown_text)

        for element in renderer.elements:
            element["source_file"] = str(Path(file_path).name)
            element["file_path"] = str(file_path)

        return renderer.elements

    def parse_markdown(self, markdown_text: str) -> MarkdownElementExtractor:
        renderer = MarkdownElementExtractor()
        markdown = mistune.create_markdown(renderer=renderer)
        markdown(markdown_text)
        return renderer

    # def extract_elements(self, markdown_text):
    #     extractor = parse_markdown_file(markdown_text)
    #     return {
    #         "headings": extractor.headings,
    #         "unordered_lists": extractor.unordered_lists,
    #         "ordered_lists": extractor.ordered_lists,
    #         "tables": extractor.tables,
    #         "links": extractor.links
    #     }

    def extract_elements(self) -> List[dict]:
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = Path(root) / file
                    elements = self.parse_markdown_file(file_path)
                    self.elements.extend(elements)
        return self.elements

    def save_to_json(self, json_path: Path):
        with Path.open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.elements, f, indent=4)

    def read_markdown_files(self, directory: Path):
        text_data = ""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):
                    with Path.open(Path(root) / file, "r", encoding="utf-8") as f:
                        text_data += f.read() + " "
        return text_data

    def clean_text(self, text):
        # Remove markdown formatting and non-alphabetic characters
        text = re.sub(r"[^\w\s]", "", text)
        return text.lower()

    def word_frequency(self, text: str):
        words = text.split()
        return Counter(words)

    def get_tables_from_text(self, markdown_text: str) -> List[str]:
        tables = []
        lines = markdown_text.split("\n")
        table = []
        in_table = False
        for line in lines:
            if line.startswith("|"):
                in_table = True
                table.append(line)
            elif in_table:
                tables.append("\n".join(table))
                table = []
                in_table = False
        return tables


# raw_text = read_markdown_files(directory_path)
# cleaned_text = clean_text(raw_text)
# word_freq = word_frequency(cleaned_text)

# # Print the word frequencies
# for word, freq in word_freq.most_common():
#     print(f'{word}: {freq}')

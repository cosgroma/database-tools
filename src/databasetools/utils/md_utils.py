"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      md_utils.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/10/2024 05:57:53
Modified By: Mathew Cosgrove
-----
"""

import re
from typing import List

import markdown


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


def get_code_blocks(markdown_string):
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
    # Extract the data from the parsed markdown.
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

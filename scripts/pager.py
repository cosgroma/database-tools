# Read page blocks json file and process it to get the page blocks.
# For each block
#   get parent, has_children, type, and type metadata and store in sublist
#   add block to unique_block_type list that stores a representative block of each type
# Output: page_id_processed_blocks.json
# Output: page_id_unique_block_types.json
import json
import os
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

import pydotplus

debug = False
MAX_LEVEL = 3


def hex_to_RGB(hex):
    """ "#FFFFFF" -> [255,255,255]"""
    # Pass 16 to the integer function for change of base
    return [int(hex[i : i + 2], 16) for i in range(1, 6, 2)]


def RGB_to_hex(RGB):
    """[255,255,255] -> "#FFFFFF" """
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#" + "".join([f"0{v:x}" if v < 16 else f"{v:x}" for v in RGB])


def color_dict(gradient):
    """Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on"""
    return {
        "hex": [RGB_to_hex(RGB) for RGB in gradient],
        "r": [RGB[0] for RGB in gradient],
        "g": [RGB[1] for RGB in gradient],
        "b": [RGB[2] for RGB in gradient],
    }


def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
    """returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    inlcuding the number sign ("#FFFFFF")"""
    # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    # Initilize a list of the output colors with the starting color
    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [int(s[j] + (float(t) / (n - 1)) * (f[j] - s[j])) for j in range(3)]
        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return color_dict(RGB_list)


gradient = linear_gradient("#f0f0f0", finish_hex="#737373", n=10)

# print(gradient)

ext_dict = {
    "": "lightgoldenrodyellow",
    ".a": "#80b1d3",
    ".bin": "#bebada",
    ".c": "#ffffb3",
    ".cloc": "antiquewhite",
    ".cls": "#fccde5",
    ".cpp": "#bebada",
    ".css": "#fdb462",
    ".dox": "#d9d9d9",
    ".elf": "#ccebc5",
    ".geom": "bisque",
    ".gitignore": "lightblue",
    ".h": "#8dd3c7",
    ".html": "lightcyan",
    ".inc": "lightgoldenrodyellow",
    ".ini": "#ffed6f",
    ".jpeg": "lightgoldenrodyellow",
    ".js": "#bc80bd",
    ".json": "#fb8072",
    ".m": "#f08b84",
    ".mat": "#ebd8ab",
    ".md": "#ccebc5",
    ".mk": "#bebada",
    ".out": "lightblue",
    ".png": "lightseagreen",
    ".py": "lightskyblue",
    ".rst": "#80b1d3",
    ".sh": "lightsalmon",
    ".so": "#bebada",
    ".sty": "#b3de69",
    ".v0": "lightsteelblue",
    ".xml": "lightyellow",
    ".yml": "#ffed6f",
}

BLOCK_TYPE_COLOR = {
    "bookmark": "lightsteelblue",
    "breadcrumb": "#80b1d3",
    "bulleted_list_item": "#bebada",
    "callout": "#ffffb3",
    "child_database": "antiquewhite",
    "child_page": "#fccde5",
    "column": "#bebada",
    "column_list": "#fdb462",
    "divider": "#d9d9d9",
    "embed": "#ccebc5",
    "equation": "bisque",
    "file": "lightblue",
    "heading_1": "#8dd3c7",
    "heading_2": "lightcyan",
    "heading_3": "lightgoldenrodyellow",
    "image": "#ffed6f",
    "link_preview": "lightgoldenrodyellow",
    "link_to_page": "#bc80bd",
    "numbered_list_item": "#fb8072",
    "paragraph": "#f08b84",
    "pdf": "#ebd8ab",
    "quote": "#ccebc5",
    "synced_block": "#bebada",
    "table": "lightsalmon",
    "table_of_contents": "lightblue",
    "table_row": "lightseagreen",
    "template": "lightskyblue",
    "to_do": "#80b1d3",
    "toggle": "lightsalmon",
    "unsupported": "#bebada",
    "video": "#b3de69",
}

SHAPE_TYPES = [
    "box",
    "circle",
    "diamond",
    "doublecircle",
    "doubleoctagon",
    "egg",
    "ellipse",
    "hexagon",
    "house",
    "invhouse",
    "invtrapezium",
    "invtriangle",
    "Mcircle",
    "Mdiamond",
    "Msquare",
    "none",
    "octagon",
    "parallelogram",
    "pentagon",
    "plaintext",
    "point",
    "polygon",
    "rect",
    "rectangle",
    "septagon",
    "trapezium",
    "triangle",
    "tripleoctagon",
]

BLOCK_TYPE_SHAPE = {
    "bookmark": "pentagon",
    "breadcrumb": "pentagon",
    "bulleted_list_item": "ellipse",
    "callout": "doublecircle",
    "child_database": "house",
    "child_page": "house",
    "column": "triangle",
    "column_list": "triangle",
    "divider": "point",
    "embed": "doubleoctagon",
    "equation": "box",
    "file": "tripleoctagon",
    "heading_1": "rectangle",
    "heading_2": "parallelogram",
    "heading_3": "diamond",
    "image": "octagon",
    "link_preview": "tripleoctagon",
    "link_to_page": "invhouse",
    "numbered_list_item": "ellipse",
    "paragraph": "ellipse",
    "pdf": "ellipse",
    "quote": "ellipse",
    "synced_block": "ellipse",
    "table": "septagon",
    "table_of_contents": "ellipse",
    "table_row": "septagon",
    "template": "ellipse",
    "to_do": "box",
    "toggle": "Msquare",
    "unsupported": "none",
    "video": "ellipse",
}


# "#b3e2cd"
# "#fdcdac"
# "#cbd5e8"
# "#f4cae4"
# "#e6f5c9"
# "#fff2ae"
# "#f1e2cc"
# "#cccccc"


def add_folder(graph, foldername, node_name, parentname=None):
    node = pydotplus.Node(
        name=node_name, shape="folder", label=foldername, fillcolor=gradient["hex"][graph["current_level"]], style="filled"
    )
    graph["dot_graph"].add_node(node)
    if parentname:
        e = pydotplus.Edge(src=parentname, dst=node_name)
        graph["dot_graph"].add_edge(e)


def add_file(graph, filename, node_name, parentname=None):
    file_extension = Path.splitext(filename)[1]
    extension = file_extension.lower()
    color = "#cccccc" if extension not in ext_dict.keys() else ext_dict[extension]
    node = pydotplus.Node(name=node_name, shape="note", label=filename, fillcolor=color, style="filled")
    graph["dot_graph"].add_node(node)
    if parentname:
        e = pydotplus.Edge(src=parentname, dst=node_name)
        graph["dot_graph"].add_edge(e)


def add_block(graph, block_type, node_name, parentname=None):
    color = BLOCK_TYPE_COLOR[block_type]
    shape = BLOCK_TYPE_SHAPE[block_type]
    node = pydotplus.Node(name=node_name, shape=shape, label=block_type, fillcolor=color, style="filled")
    graph["dot_graph"].add_node(node)
    if parentname:
        e = pydotplus.Edge(src=parentname, dst=node_name)
        graph["dot_graph"].add_edge(e)


def process_path(root_path, graph, max_level):
    graph["current_level"] += 1
    if graph["current_level"] > max_level:
        graph["current_level"] -= 1
        return
    # basename = Path(root_path).name
    if debug:
        print(f"process_path: {root_path}")
    for obj in os.listdir(root_path):
        obj_path = root_path + "/" + obj
        parentname = "_".join(graph["tree_history"])
        obj_node_name = "_".join(graph["tree_history"])
        obj_node_name += "_" + obj
        if ".git" in obj or "build" in obj or ".dep" in obj or ".archive" in obj or ".backup" in obj:
            continue
        if Path.is_dir(obj_path):
            parentname = "_".join(graph["tree_history"])
            graph["tree_history"].append(obj)
            if debug:
                print(f"add_folder: {obj_node_name}\n\tparentname: {parentname}")
            add_folder(graph, obj, obj_node_name, parentname=parentname)
            process_path(obj_path, graph, max_level)
            graph["tree_history"].pop()
            if debug:
                tree_history_name = "_".join(graph["tree_history"])
                print(f"\tparentname now: {tree_history_name}")
        else:
            if graph["dirs-only"] or obj == "temp.dot":
                continue
            if debug:
                print(f"add_file: {obj_node_name}\n\tparentname: {parentname}")
            add_file(graph, obj, obj_node_name, parentname=parentname)

    graph["current_level"] -= 1


def make_dir_graph(arguments):
    if arguments["PATH"]:
        if Path.is_dir(Path(arguments["PATH"])):
            root_path = Path(arguments["PATH"])
    else:
        root_path = Path.cwd()
    max_level = int(arguments["--level"])
    tree_history = root_path.parts
    home_index = tree_history.index("home")
    tree_history = tree_history[home_index:]
    graph = {
        "dot_graph": pydotplus.Dot(graph_type="graph"),
        "current_level": 0,
        "tree_history": tree_history,
        "dirs-only": arguments["--dirs-only"],
    }
    graph["dot_graph"].set("rankdir", "LR")
    # graph["dot_graph"].set("rankdir", "TD")
    graph["dot_graph"].set("splines", "ortho")
    basename = Path(root_path).name
    obj_node_name = "_".join(graph["tree_history"])
    add_folder(graph, basename, obj_node_name)
    process_path(root_path, graph, max_level)
    return graph


class TreeNode:
    def __init__(self, block_id: str, parent_id: str, block_type: str, block_metadata: Dict[str, Any]):
        self.block_id = block_id
        self.parent_id = parent_id
        self.block_type = block_type
        self.block_metadata = block_metadata
        self.children: List["TreeNode"] = []
        self.parent = None

    def add_child(self, child: "TreeNode"):
        self.children.append(child)
        child.parent = self

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.block_id) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

    def __str__(self):
        return self.__repr__()


# Read page blocks json file
def read_page_blocks(page_blocks_file):
    with Path.open(page_blocks_file) as f:
        page_blocks = json.load(f)
    return page_blocks


important_key_list = ["id", "parent", "has_children", "type"]


def get_unique_block_types(page_blocks):
    unique_block_types = {}
    for block in page_blocks:
        block_type = block["type"]
        if block_type not in unique_block_types.keys():
            unique_block_types[block_type] = block[block_type]
    return unique_block_types


# Process page blocks
def process_page_blocks(page_blocks):
    processed_blocks = []
    for block in page_blocks:
        block_redacted = {k: v for k, v in block.items() if k in important_key_list}
        if block["has_children"]:
            block_redacted["children"] = process_page_blocks(block["children"])
        block_type = block_redacted["type"]
        block_redacted[block_type] = block[block_type]
        processed_blocks.append(block_redacted)
    return processed_blocks


# Write processed page blocks to file
def write_processed_page_blocks(page_id, processed_blocks, page_dir):
    processed_blocks_file = f"{page_dir}/{page_id}_processed_blocks.json"
    with Path.open(processed_blocks_file, "w") as f:
        json.dump(processed_blocks, f)
    return processed_blocks_file


# Write unique block types to file
def write_unique_block_types(page_id, unique_block_types, page_dir):
    unique_block_types_file = f"{page_dir}/{page_id}_unique_block_types.json"
    with Path.open(unique_block_types_file, "w") as f:
        json.dump(unique_block_types, f)
    return unique_block_types_file


# if __name__ == "__main__":
#     arguments = docopt(__doc__)
#     # print(arguments)
#     # print(arguments)
#     main(arguments)
#     graph = make_dir_graph(arguments)
# print(graph["dot_graph"].to_string())


# Main
def main():
    page_blocks_file = sys.argv[1]
    file_name_no_ext, file_extension = Path.splitext(page_blocks_file)

    page_id = Path.basename(file_name_no_ext)
    page_dir = Path.dirname(page_blocks_file)
    page_blocks = read_page_blocks(page_blocks_file)

    processed_blocks = process_page_blocks(page_blocks)
    processed_blocks_file = write_processed_page_blocks(page_id, processed_blocks, page_dir)
    print(f"Processed blocks: {processed_blocks_file}")

    unique_block_types = get_unique_block_types(page_blocks)
    unique_block_types_file = write_unique_block_types(page_id, unique_block_types, page_dir)
    print(f"Unique block types: {unique_block_types_file}")


if __name__ == "__main__":
    main()

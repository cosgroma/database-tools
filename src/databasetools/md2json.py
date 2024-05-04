import json
from pathlib import Path
from typing import List
from typing import Union


class Noop:
    pass


noop = Noop()

rules = []


def rule(func):
    rules.append(func)
    return func


class MdToJsonConverter:
    def __init__(self, strip_meta_chars=None):
        self.stripchars = strip_meta_chars

    def convert(self, md_dir: Union[str, Path], json_dir: Union[str, Path]):
        """Convert markdown to Notion JSON."""
        try:
            md_dir = Path(md_dir)
            md_dir.mkdir(parents=True, exist_ok=True)

            json_dir = Path(json_dir)
            json_dir.mkdir(parents=True, exist_ok=True)

        except OSError as e:
            if not md_dir.exists() and not json_dir.exists():
                raise e

        paths = list(Path.glob(md_dir, "*.md"))
        for path in paths:
            with Path.open(path) as f:
                markdown = f.read()
                page_id = Path(path).stem
                path = json_dir / f"{page_id}.json"
                blocks = self.md2json(markdown)
                with Path.open(path, "w") as f:
                    json.dump(blocks, f, indent=2)

                if len(paths) == 1:
                    return path

        return json_dir


class MdToJson:
    def __init__(self, strip_meta_chars=None):
        self.stripchars = strip_meta_chars

    def md2json(self, markdown: str) -> List[dict]:
        """Convert markdown to Notion JSON."""
        blocks = []
        for line in markdown.splitlines():
            for rule in rules:
                if (block := rule(self, line)) is not noop:
                    blocks.append(block)
                    break
            else:
                raise NotImplementedError(f"Unsupported markdown: {line}")
        return blocks

    @rule
    def apply_heading(self, line):
        if line.startswith("# "):
            return {"type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}}
        return noop

    @rule
    def apply_paragraph(self, line):
        return {"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}}

    @rule
    def apply_callout(self, line):
        return {
            "type": "callout",
            "callout": {"icon": line.split()[0], "rich_text": [{"type": "text", "text": {"content": line.split()[1]}}]},
        }

    @rule
    def apply_bookmark(self, line):
        return {"type": "bookmark", "bookmark": {"url": line.split()[1]}}

    @rule
    def apply_divider(self, line):
        return {"type": "divider"}

    @rule
    def apply_item(self, line):
        if line.startswith("- "):
            return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}}
        return noop

    @rule
    def apply_quote(self, line):
        if line.startswith("> "):
            return {"type": "quote", "quote": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}}
        return noop

    @rule
    def apply_to_do(self, line):
        if line.startswith("- [ ] "):
            return {"type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": line[6:]}}]}}
        return noop

    @rule
    def apply_code(self, line):
        if line.startswith("```"):
            return {"type": "code", "code": {"language": line[3:], "rich_text": [{"type": "text", "text": {"content": line[3:]}}]}}
        return noop

    @rule
    def apply_table(self, line):
        return {"type": "table", "table": {"children": []}}

    @rule
    def apply_image(self, line):
        if line.startswith("!["):
            return {"type": "image", "image": {"caption": line.split("]")[0][2:], "url": line.split("(")[1][:-1]}}
        return noop

    @rule
    def apply_toggle(self, line):
        if line.startswith("<details>"):
            return {"type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": line[9:]}}]}}
        return noop

    @rule
    def apply_math(self, line):
        if line.startswith("$$"):
            return {"type": "equation", "equation": {"expression": line[2:]}}
        return noop

    @rule
    def apply_misc(self, line):
        return {"type": "misc", "misc": {"content": line}}

    @rule
    def apply_text(self, line):
        return {"type": "text", "text": {"content": line}}

import re
from re import Match

IMAGE_PATTERN = re.compile(r"""<img src="((?:\w+\/)*(\w+).(\w+))"\s*alt="(\w+)"\s*\/>""")


def html_image_2_cf_image(html_string: str):
    def repl(m: Match):
        return f"""<ac:image ac:alt="{m.group(4)}"><ri:attachment ri:filename="{m.group(2)}.{m.group(3)}" /></ac:image>\n"""

    result = re.sub(IMAGE_PATTERN, repl, html_string)
    return result


def space_out_tables(markdown: str) -> str:
    TABLE_PATTERN = r"((?:\|.*){1}\n(?:(?:\|\w*:?\w*-+\w*:?\w*)+\|)(?:\n\|.*)+)"

    def replace(m: re.Match):
        return f"""\n\n{m.group(0)}\n\n"""

    return re.sub(TABLE_PATTERN, replace, markdown)

import re
from re import Match

IMAGE_PATTERN = re.compile(r"""<img src="((?:\w+\/)+(\w+).(\w+))"\s*alt="(\w+)"\s*\/>""")


def image2cf(html_string: str):
    def repl(m: Match):
        return f"""<ac:image ac:alt="{m.group(4)}"><ri:attachment ri:filename="{m.group(2)}.{m.group(3)}" /></ac:image>\n"""

    result = re.sub(IMAGE_PATTERN, repl, html_string)
    return result

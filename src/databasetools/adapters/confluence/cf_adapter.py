import re
from re import Match

REVERSE_BOLDED_LISTS = re.compile(r"""\*\*(\d+)\.\s(.+)\*\*""")
CONJOINED_TABLE_PATTERN = re.compile(
    r"""(?:\|[^\|\n]*)+\|\n(?:\|:?-+:?)+\|\n(?:(?:(?:\|[^\|\n]*)+\|\n)+(?=(?:\|[^\|\n]*)+\|\n(?:\|:?-+:?)+\|\n))"""
)  # WARNING POSSIBLE CATASTROPHIC BACKTRACKING (until someone tests it more...)
TABLE_PATTERN = re.compile(r"((?:\|.*){1}\n(?:(?:\|\w*:?\w*-+\w*:?\w*)+\|)(?:\n\|.*)+)")
HTML_TABLE_PATTERN = re.compile(r"""<table>.*?</table>""")

IMAGE_PATTERN = re.compile(r"""<img src="((?:\w+\/)*(\w+).(\w+))"\s*alt="(.*?)"\s*\/>""")
PPTX_PATTERN = re.compile(r"""<a\s+href\s*=\s*"(\w+?\.pptx)"\s*>(.*?)<\/a>""")
PDF_PATTERN = re.compile(r"""<a\s+href\s*=\s*"(\w+?\.pdf)"\s*>(.*?)<\/a>""")
XLS_PATTERN = re.compile(r"""<a\s+href\s*=\s*"(\w+?\.(?:xls|xlsx))"\s*>(.*?)<\/a>""")
DOCX_PATTERN = re.compile(r"""<a\s+href\s*=\s*"(\w+?\.(?:docx|doc))"\s*>(.*?)<\/a>""")

LINK_IN_BRACKET = re.compile(r"""<(?:\bhttps?://([^>]+)\b)>""")
INVALID_HTML_TAGS = [LINK_IN_BRACKET]


def find_invalid_html(markdown: str) -> str:
    def repl(m: re.Match):
        return f"""&lt;{m.group(1)}&gt;"""

    for regx in INVALID_HTML_TAGS:
        markdown = re.sub(regx, repl, markdown)
    return markdown


def reverse_bolded_lists(markdown: str) -> str:
    def repl(m: re.Match):
        return f"""{m.group(1)}. **{m.group(2)}**"""

    return re.sub(REVERSE_BOLDED_LISTS, repl, markdown)


def space_out_tables(markdown: str) -> str:
    regx_todo = [HTML_TABLE_PATTERN, TABLE_PATTERN, CONJOINED_TABLE_PATTERN]

    def repl(m: re.Match):
        return f"""\n\n{m.group(0)}\n\n"""

    for regx in regx_todo:
        markdown = re.sub(regx, repl, markdown)
    return markdown


def html_image_2_cf_image(html_string: str) -> str:
    def repl(m: Match):
        return f"""<ac:image ac:alt="{m.group(4)}"><ri:attachment ri:filename="{m.group(2)}.{m.group(3)}" /></ac:image>\n"""

    result = re.sub(IMAGE_PATTERN, repl, html_string)
    return result


def html_pdf_link_2_cf_pdf(html_string: str) -> str:
    def repl(m: Match):
        return f"""<p>{m.group(2)}</p><ac:structured-macro ac:name="viewpdf"><ac:parameter ac:name="name"><ri:attachment ri:filename="{m.group(1)}" /></ac:parameter></ac:structured-macro>"""

    return re.sub(PDF_PATTERN, repl, html_string)


def html_pptx_link_2_cf_pptx(html_string: str) -> str:
    def repl(m: Match):
        return f"""<p>{m.group(2)}</p><ac:structured-macro ac:name="viewppt"><ac:parameter ac:name="name"><ri:attachment ri:filename="{m.group(1)}" /></ac:parameter></ac:structured-macro>"""

    return re.sub(PPTX_PATTERN, repl, html_string)


def html_xls_link_2_cf_xls(html_string: str) -> str:
    def repl(m: Match):
        return f"""<p>{m.group(2)}</p><ac:structured-macro ac:name="viewxls"><ac:parameter ac:name="name"><ri:attachment ri:filename="{m.group(1)}" /></ac:parameter></ac:structured-macro>"""

    return re.sub(XLS_PATTERN, repl, html_string)


def html_docx_link_2_cf_docx(html_string: str) -> str:
    def repl(m: Match):
        return f"""<p>{m.group(2)}</p><ac:structured-macro ac:name="viewdoc"><ac:parameter ac:name="name"><ri:attachment ri:filename="{m.group(1)}" /></ac:parameter></ac:structured-macro>"""

    return re.sub(DOCX_PATTERN, repl, html_string)


def add_attachments_macro(html_string: str) -> str:
    return html_string + r"""<p><ac:structured-macro ac:name="attachments" /></p>"""


PRE_PROCESS_FUNCS = [find_invalid_html, reverse_bolded_lists, space_out_tables]


def cf_pre_process(markdown: str) -> str:
    """Runs pre "docblocking" hooks. Should be run before converting markdown into docblocks.

    Args:
        markdown (str): Markdown string to check.

    Returns:
        str: Formatted string.
    """
    for func in PRE_PROCESS_FUNCS:
        print(f"\t\t\tBegin Preprocess... ({func.__name__})")
        markdown = func(markdown)
        print("\t\t\tFinished Preprocess")
    return markdown


POST_PROCESS_FUNCS = [
    html_image_2_cf_image,
    html_pptx_link_2_cf_pptx,
    html_xls_link_2_cf_xls,
    html_pdf_link_2_cf_pdf,
    html_docx_link_2_cf_docx,
    add_attachments_macro,
]


def cf_post_process(html_string: str) -> str:
    """Runs post processing hooks to check html strings and format them for confluence style xml

    Args:
        html_string (str): Original html string to be uploaded to confluence.

    Returns:
        str: Confluence compatible html string.
    """
    for func in POST_PROCESS_FUNCS:
        print(f"\t\t\tBegin Post_Process... ({func.__name__})")
        html_string = func(html_string)
        print("\t\t\tFinished Post-Processing")
    return html_string

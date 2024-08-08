import unittest

import databasetools.adapters.confluence.cf_adapter as cf


class TestCFAdapter(unittest.TestCase):
    def test_html_pptx_link_2_cf_pptx(self):
        test_str = (
            """<p><a href="https://confluence.northgrum.com/cac37417528a4512b83e7360eed7e93e.pptx">FTUAS Agenda 20220331.pptx</a></p>"""
        )

        result = cf.html_pptx_link_2_cf_pptx(test_str)
        print(result)

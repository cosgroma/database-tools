cat tox_cmds.sh
pip install tox
tox
tox -v -e single  -- -x ./tests/test_notion.py
tox -v -e single  -- -x ./tests/test_utils.py
tox -v -e single  -- -x ./tests/test_utils.py::test_get_tables_from_text
tox -v -e single  -- -x ./tests/test_utils.py::test_word_frequency

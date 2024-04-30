import subprocess


def test_main():
    assert subprocess.check_output(["dbman", "foo", "foobar"], text=True) == "foobar\n"

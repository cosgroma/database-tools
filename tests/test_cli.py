import subprocess


def test_main():
    assert subprocess.check_output(["db-man", "--help"], text=True).startswith("Usage:")

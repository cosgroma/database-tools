import subprocess


def test_main():
    assert subprocess.check_output(["dbman", "-h"], text=True).startswith("Usage:")

import pathlib


def test_no_print_statements():
    for path in pathlib.Path('.').rglob('*.py'):
        if path.name == 'app.py' or path.parts[0] == 'tests':
            continue
        text = path.read_text()
        assert 'print(' not in text, f"Forbidden print found in {path}"


import pathlib


def documentation() -> dict:
    """Dict with name -> path to markdown file.

    If name contains a single '/' it will be shown in a submenu. Multiple '/' are not allowed.
    The insertion order is mostly preserved (folders are grouped in the menu)."""
    return {}

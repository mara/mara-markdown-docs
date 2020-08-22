# Mara Markdown Documentation

Display markdown documentation in mara UI

[![Build Status](https://travis-ci.org/jankatins/mara-markdown-docs.svg?branch=master)](https://travis-ci.org/jankatins/mara-markdown-docs)
[![PyPI - License](https://img.shields.io/pypi/l/mara-markdown-docs.svg)](https://github.com/jankatins/mara-markdown-docs/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/mara-markdown-docs.svg)](https://badge.fury.io/py/mara-markdown-docs)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://communityinviter.com/apps/mara-users/public-invite)


This package displays configured documentation in markdown format in the UI:

- Convert markdown to html via [markdown-it](https://github.com/markdown-it/markdown-it)
- Supports a folder structure in the menu
- Supports [mermaid](https://mermaid-js.github.io/mermaid/#/) diagrams

&nbsp;

## Installation

To use the library directly, use pip:

```
pip install git+https://github.com/jankatins/mara-markdown-docs.git
```

&nbsp;

## Configuration

Assuming you configure via `app/setup_docs.py`:

```python
"""Configures the docs functionality"""

import pathlib
from mara_app.monkey_patch import patch

import mara_markdown_docs.config

@patch(mara_markdown_docs.config.documentation)
def documentation() -> dict:
    """Dict with name -> path to markdown file.

    If name contains a single '/' it will be shown in a submenu. Multiple '/' are not allowed.
    The insertion order is mostly preserved (folders are grouped in the menu)."""

    repo_root_dir = pathlib.Path(__file__).parent.parent

    # Cases matter in path!
    docs = {
        'Pipeline/Marketing': repo_root_dir / 'app/pipelines/marketing/README.md',
        'Developer/Setup': repo_root_dir / 'README.md',
        'Developer/Code Conventions': repo_root_dir / 'code_conventions.md',
    }

    return docs
```

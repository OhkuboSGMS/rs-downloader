# rs-downloader

Download records from R S share site.


`````
rye run python -m rs_downloader 
---
NAME
    __main__.py

SYNOPSIS
    __main__.py PROJECTS_URL PARENT_DIR <flags>

POSITIONAL ARGUMENTS
    PROJECTS_URL
        Type: str
    PARENT_DIR
        Type: str

FLAGS
    -m, --memo_path=MEMO_PATH
        Type: str
        Default: 'memo.json'
    -t, --timeout=TIMEOUT
        Type: int
        Default: 30000

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```
import contextlib
import json
import os
from collections.abc import Callable


@contextlib.asynccontextmanager
async def go_and_back(page, action: Callable, wait_time: int = 0):
    await action()
    yield page
    if wait_time:
        await page.wait_for_timeout(wait_time)
    await page.go_back()


@contextlib.contextmanager
def open_json(
    json_path: str, encoding: str = "UTF-8", indent: int = 2, ensure_ascii: bool = False
):
    _json_dict = {}
    if not os.path.exists(json_path):
        yield _json_dict
    else:
        with open(json_path, encoding=encoding) as fp:
            _json_dict = json.load(fp)
            yield _json_dict

    with open(json_path, "w", encoding=encoding) as fp:
        json.dump(_json_dict, fp, indent=indent, ensure_ascii=ensure_ascii)

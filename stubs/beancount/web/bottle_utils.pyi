from typing import Any

class AttrMapper:
    mapper_function: Any = ...
    def __init__(self, mapper_function: Any) -> None: ...
    def __getattr__(self, name: Any): ...
    def build(self, *args: Any, **kwargs: Any): ...

itertools: Any

def internal_redirect(app: Any, path_depth: Any): ...

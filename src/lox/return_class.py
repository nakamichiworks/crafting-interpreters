from typing import Any


class Return(Exception):
    def __init__(self, value: Any, *args: object) -> None:
        super().__init__(*args)
        self.value = value

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Logger:
    enabled: bool = True

    def log(self, *args):
        if self.enabled:
            print(*args)

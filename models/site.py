from dataclasses import dataclass


@dataclass
class Site:
    code: str
    name: str
    host: str
    port: int
    database: str

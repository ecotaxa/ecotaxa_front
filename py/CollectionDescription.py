from typing import List

from dataclasses import dataclass


@dataclass
class CollectionDescription:
    ref: str
    provider: str
    title: str
    projects: List[int]
    contact: str
    license: str
    abstract: str
    description: str
    creators: str
    associates: str
    citation: str
    geographical: str


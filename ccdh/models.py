from dataclasses import dataclass


@dataclass
class DataElement(object):
    context: str
    entity: str
    attribute: str
    
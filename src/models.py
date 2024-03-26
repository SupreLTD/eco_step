from dataclasses import dataclass


@dataclass(slots=True)
class Item:
    title: str = ''
    article: str = ''
    price: str = ''
    images: str = ''
    description: str = ''
    options: str = ''
    cat: str = ''
    url: str = ''

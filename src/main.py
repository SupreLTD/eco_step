from pprint import pprint

from aiohttp import ClientSession

from .config import HEADERS, URLS
from .utils import get_items_link,get_data


async def main():
    async with ClientSession(headers=HEADERS) as session:
        for URL in URLS:
            links = await get_data(session, URL)
            # pprint(links)




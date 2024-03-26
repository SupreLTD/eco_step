
from aiohttp import ClientSession
from tqdm import tqdm

from .config import HEADERS, URLS, URLS2
from .utils import get_data, write_to_excel


async def main():
    items = []
    async with ClientSession(headers=HEADERS) as session:
        for URL in tqdm(URLS):
            data = await get_data(session, URL, -2)
            items.extend(data)
            break
        for URL in tqdm(URLS2):
            data = await get_data(session, URL, -3)
            items.extend(data)
    write_to_excel(items)





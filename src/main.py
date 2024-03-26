from aiohttp import ClientSession

from .config import HEADERS, URLS


async def main():
    async with ClientSession(headers=HEADERS) as session:
        for URL in URLS:
            pass

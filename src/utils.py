from aiohttp import ClientSession, ClientResponse
from bs4 import BeautifulSoup
from tenacity import retry
from loguru import logger


async def get_html(session: ClientSession, url: str) -> ClientResponse.text:
    async with session.get(url) as response:
        logger.info(f'{response.status} | {url}')
        assert response.status == 200
        return await response.text()


async def get_items_link(session: ClientSession, url: str) -> list:
    data = []
    category = None

def parse_links(soup: BeautifulSoup):
    pass
import asyncio

from aiohttp import ClientSession, ClientResponse
from bs4 import BeautifulSoup
from tenacity import retry
from loguru import logger


@retry
async def get_html(session: ClientSession, url: str) -> ClientResponse.text:
    async with session.get(url) as response:
        logger.info(f'{response.status} | {url}')
        assert response.status == 200
        return await response.text()


async def get_items_link(session: ClientSession, url: str) -> list:
    links = []
    for i in range(1, 1000):
        link = f"{url}/{i}.html?tmpl=ajax"
        response_data = await get_html(session, link)
        # print(response_data.strip())
        if not response_data.strip():
            break
        links.extend(parse_links(BeautifulSoup(response_data, 'lxml')))

    return links


def parse_links(soup: BeautifulSoup):
    data = soup.find_all('h3')
    data = [f"https://xn----8sbgjyicscimifi4nb5b.xn--p1ai{i.find('a')['href']}" for i in data]
    return data


async def get_data(session: ClientSession, url: str):
    tasks = []
    for link in await get_items_link(session, url):
        tasks.append(asyncio.create_task(parse_data(session, link)))
    await asyncio.gather(*tasks)


async def parse_data(session: ClientSession, url):
    soup = BeautifulSoup(await get_html(session, url), 'lxml')
    title = soup.find('h2', class_='first').text
    article = soup.find('ul', class_='list-unstyled').find('strong').text
    price = soup.find('span', id='price').text
    images = soup.find_all('div', class_='item text-center')
    images = [i.find('a')['href'] for i in images]
    description = soup.find('div', id='tab-description').text
    options = soup.find('div', id='tab-specification').find_all('tr')
    options = ', '.join([': '.join([j.text for j in i.find_all('td')]) for i in options])
    cat = soup.find('ol', class_='breadcrumb').find_all('li')[-2].text

    print(title, article, price, images, description, options, cat, sep='\n\n')

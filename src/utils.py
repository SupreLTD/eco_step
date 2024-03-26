import asyncio

from aiohttp import ClientSession, ClientResponse
from bs4 import BeautifulSoup
from tenacity import retry
from loguru import logger
from funcy import chunks
import pandas as pd

from .models import Item


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


async def get_data(session: ClientSession, url: str, cat: int):
    data = []
    for chunk in list(chunks(10, await get_items_link(session, url))):
        tasks = []
        for link in chunk:
            tasks.append(asyncio.create_task(parse_data(session, link, cat)))
        data += await asyncio.gather(*tasks)
    return data


async def parse_data(session: ClientSession, url, cat: int):
    soup = BeautifulSoup(await get_html(session, url), 'lxml')
    title = soup.find('h2', class_='first').text
    article = soup.find('ul', class_='list-unstyled').find('strong').text
    price = soup.find('span', id='price').text
    images = soup.find_all('div', class_='item text-center')
    images = [i.find('a')['href'] for i in images]
    images.append(f"https://xn----8sbgjyicscimifi4nb5b.xn--p1ai{soup.find('a', id='picture_orig')['href']}")
    images = ', '.join(images)
    description = soup.find('div', id='tab-description').text
    options = soup.find('div', id='tab-specification').find_all('tr')
    options = ', '.join([': '.join([j.text for j in i.find_all('td')]) for i in options])
    cat = soup.find('ol', class_='breadcrumb').find_all('li')[cat].text

    return Item(
        title=title,
        article=article,
        price=price,
        images=images,
        description=description,
        options=options,
        cat=cat,
        url=url
    )


def write_to_excel(data: list[Item]):
    columns = ['Название', 'Артикул', 'Цена', 'Изображения', 'Описание', 'Характеристики', 'Раздел', 'Ссылка']
    data = [[i.title, i.article, i.price, i.images, i.description, i.options, i.cat, i.url] for i in data]
    df = pd.DataFrame(data, columns=columns)
    df.to_excel('eco_step.xlsx', index=False)

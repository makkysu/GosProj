from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import asyncio

from sqlalchemy import select

from app.core.database import Session
from app.models.laws import Laws
from app.models.categories import Categories
from app.models.law_categories import LawCategories

async def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url)
        return response.text

def parse_laws(html):
    soup = BeautifulSoup(html, 'html.parser')
    laws = []
    
    for doc in soup.select('div.doc'):
        a = doc.select_one('a')
        title = a.get_text() if a else None
        url = a.get('href') if a else None
        doccard = doc.select_one('div.doc-card span')
        date_str = doccard.get_text() if doccard else None
        date = datetime.strptime(date_str, '%d.%m.%Y').date() if date_str else None
        strong = doc.select_one('strong')
        number = strong.get_text() if strong else None
        b = doc.select_one('small b')
        status = b.get_text() if b else None
        rada_id = url.split('/show/')[-1] if url else None
        print(f"rada_id: {rada_id}, url: {url}")

        laws.append({"title": title, "url": url, "date": date, "number": number, "status": status, "rada_id": rada_id})
    return laws

async def save_laws(laws, slug):
    async with Session() as session:
        category = (await session.execute(select(Categories).where(Categories.slug == slug))).scalar_one_or_none()
        for law in laws:
            l = Laws(
            title=law['title'],
            url=law['url'],
            date_adopted=law['date'],
            number=law['number'],
            status=law['status'],
            rada_id=law['rada_id']
            )
            session.add(l)
            await session.flush() 
            if category:
                lc = LawCategories(
                    law_id=l.id,
                    category_id = category.id
                )
                session.add(lc)
        await session.commit()


async def run():
    slugs = ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100', '110', '120', '130', '140', '150', '160', '170', '180', '190', '200', '210', '220', '230', '240', '250', '260', '270', '280']

    for slug in slugs:

        page = 1
        print('Parsing start...')

        while True:
            url = f"https://zakon.rada.gov.ua/laws/main/klas{slug}/page"
            url += (str(page) if page > 1 else "")
            print(f'Loading page: {url}')
            html = await fetch_page(url)
            laws = parse_laws(html)
            print(f'Found laws: {len(laws)}')
            if not laws:
                break
            await save_laws(laws, slug)
            page += 1

asyncio.run(run())

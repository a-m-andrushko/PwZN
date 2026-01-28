import requests
from bs4 import BeautifulSoup
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE_URL = 'https://webscraper.io'   # LEGAL, made for scraping
START_URL = 'https://webscraper.io/test-sites/e-commerce/static/computers/laptops'

def get_product_links():   # get product links and append them to an array
    response = requests.get(START_URL)

    soup = BeautifulSoup(response.text, 'html.parser')

    links = []

    for a in soup.select('a.title'):
        href = a.get('href')
        if href:
            links.append(BASE_URL + href)

    return links


def parse_product(url):   # scrape content for each product
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.select_one('h4.title').get_text(strip=True)
    price = soup.select_one('h4.price').get_text(strip=True)
    description = soup.select_one('p.description').get_text(strip=True)

    return {
        'title': title,
        'price': price,
        'description': description,
        'url': url
    }


if __name__ == '__main__':
    product_links = get_product_links()
    parsed_products = []

    with ProcessPoolExecutor(multiprocessing.cpu_count()) as executor:   # a pool of processes for as many cores as there are in the CPU
        futures = [executor.submit(parse_product, url) for url in product_links]   # 'future' guarantees that some result will eventually be returned
        for future in as_completed(futures):   # loop over results ('futures') once all 'futures' are done
            parsed_products.append(future.result())   # append 'futures' to an array

    with open('laptops.json', 'w', encoding='utf-8') as f:   # dump results to a .json
        json.dump(parsed_products, f, indent=2, ensure_ascii=False)
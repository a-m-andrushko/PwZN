from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import argparse
import json

parser = argparse.ArgumentParser(description='This is a script for dynamic web-scraping')
parser.add_argument('-f', '--filename', help='JSON filename to store scraped data')
args = parser.parse_args()

url = 'https://webscraper.io/test-sites/e-commerce/scroll'   # LEGAL, made for scraping

options = Options()
service = Service('geckodriver.exe')   # Firefox driver
driver = webdriver.Firefox(service=service, options=options)
driver.get(url)

time.sleep(3)

computers_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/test-sites/e-commerce/scroll/computers']"))
)
computers_button.click()   # click 'Computers' button

time.sleep(3)

laptops_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/test-sites/e-commerce/scroll/computers/laptops']"))
)
laptops_button.click()   # click 'Laptop' button inside 'Computers'

time.sleep(3)

for _ in range(3):   # scroll and load more content 3 times
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(3)


products = []   # create an empty array to store products' data

product_cards = driver.find_elements(By.CSS_SELECTOR, 'div.thumbnail')   # locate all product cards currently loaded

for card in product_cards:
    title = card.find_element(By.CSS_SELECTOR, 'a.title').text   # scrape product title
    description = card.find_element(By.CSS_SELECTOR, 'p.description').text   # scrape product description
    price = card.find_element(By.CSS_SELECTOR, 'h4.price').text   # scrape product price
    reviews = card.find_element(By.CSS_SELECTOR, 'div.ratings p.pull-right').text   # scrape number of product reviews
    
    products.append({   # write data to the dictionary
        'title': title,
        'description': description,
        'price': price,
        'reviews': reviews
    })

with open(f'{args.filename}.json', 'w') as f:   # write the dictionary in the .json format
    json.dump(products, f, indent=4)

driver.quit()
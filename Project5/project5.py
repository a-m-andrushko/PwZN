import argparse
import requests
from bs4 import BeautifulSoup
import json

parser = argparse.ArgumentParser(description='This is a script for static web-scraping')
parser.add_argument('-f', '--filename', help='JSON filename to store scraped data')
args = parser.parse_args()

url = 'https://www.scrapethissite.com/pages/simple/'   # LEGAL, made for scraping

res = requests.get(url)

soup = BeautifulSoup(res.text, 'html.parser')

countries_data = soup.find_all('div', class_ = 'col-md-4 country')   # fetch a div with all country data

countries = {}   # create an empty dictionary to store countries data

for country in countries_data:
    name = country.find('h3', class_='country-name').get_text(strip=True)   # scrape country name
    capital = country.find('span', class_='country-capital').get_text(strip=True)   # scrape country capital
    population = country.find('span', class_='country-population').get_text(strip=True)   # scrape country population
    area = country.find('span', class_='country-area').get_text(strip=True)   # scrape country area

    countries[name] = {   # write data to the dictionary
        'Capital': capital,
        'Population': population,
        'Area (km^2)': area
    }


with open(f'{args.filename}.json', 'w') as f:   # write the dictionary in the .json format
    json.dump(countries, f, indent=4)
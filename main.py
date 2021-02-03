from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm_notebook

import requests
import json

# pages to parse
pages = [
    'https://www.allsides.com/media-bias/media-bias-ratings',
    'https://www.allsides.com/media-bias/media-bias-ratings?page=1',
    'https://www.allsides.com/media-bias/media-bias-ratings?page=2'
]

# logic for the rating


def get_agreeance_text(ratio):
    if ratio > 3:
        return "absolutely agrees"
    elif 2 < ratio <= 3:
        return "strongly agrees"
    elif 1.5 < ratio <= 2:
        return "agrees"
    elif 1 < ratio <= 1.5:
        return "somewhat agrees"
    elif ratio == 1:
        return "neutral"
    elif 0.67 < ratio < 1:
        return "somewhat disagrees"
    elif 0.5 < ratio <= 0.67:
        return "disagrees"
    elif 0.33 < ratio <= 0.5:
        return "strongly disagrees"
    elif ratio <= 0.33:
        return "absolutely disagrees"
    else:
        return None


def scrape_allsides_tables(data):\

    print('Scraping tables...')

    for page in pages:
        r = requests.get(page)

        # create new instance of BS
        soup = BeautifulSoup(r.content, 'html.parser')

        # selecting the table containing the information
        rows = soup.select('tbody tr')

        for row in rows:
            d = dict()

            # getting the name of the first news outlet
            d['name'] = row.select_one('.source-title').text.strip()

            # we needed to acces the attribute href (doing so by [])
            d['allsides_pages'] = 'https://www.allsides.com' + \
                row.select_one('.source-title a')['href']

            # bias (taken from the url in href)
            d['bias'] = row.select_one(
                '.views-field-field-bias-image a')['href'].split('/')[-1]

            # community feedback (f at start is to inser variables into string and .2f is for rounding floats in python)
            d['agree'] = int(row.select_one('.agree').text)
            d['disagree'] = int(row.select_one('.disagree').text)
            d['agree_ratio'] = d['agree']/d['disagree']
            d['agreeance_text'] = get_agreeance_text(d['agree_ratio'])

            data.append(d)

        sleep(10)  # wait 10 seconds to send next request

    return data


def scrape_allsides_sources(data):

    print('Scraping sources...')

    # get the website of the news outlet, if no website exists, ignore the error
    for d in tqdm_notebook(data):
        r = requests.get(d['allsides_pages'])
        soup = BeautifulSoup(r.content, 'html.parser')

        try:
            website = soup.select_one('.www')['href']
            d['website'] = website

        except TypeError:
            pass

        sleep(10)
    return data


def save_json(data):
    with open('allsides.json', 'w') as file:
        json.dump(data, file)


def open_json(data):
    with open('allsides.json', 'r') as file:
        json.load(file)


def main():
    data = []
    data = scrape_allsides_tables
    data = scrape_allsides_sources
    save_json(data)

    print('Done.')


if __name__ == '__main___':
    main()

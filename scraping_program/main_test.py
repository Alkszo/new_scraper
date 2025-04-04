from page_scrapper import page_scrapper
from url_scrapper import url_scrapper
import requests
import csv
from tqdm import tqdm
import os.path

page_names = []
with open('page_names.csv', newline='') as f:
    reader = csv.reader(f)    
    for entry in reader:
        page_names.append(entry[0])

page_names = page_names[:10]

#defining requests session
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}
session = requests.Session()
session.headers = headers

def main_scrapper(input_name, output_data_name, output_url_name, output_fail_name, session):


    field_names = ['immo_id', 'zip_code', 'province', 'price', 'subtype_of_property', 'building_condition', 'living_area', 'year_of_construction', 'energy_certificate', 'geolocation', 
                'equipped_kitchen', 'bedroom_nr', 'swimming_pool', 'terrace', 'garden', 'plot_surface', 'url']

    if os.path.isfile(f'../scraping_results/{output_data_name}.csv') == False:
        with open(f'../scraping_results/{output_data_name}.csv', 'a', newline='') as file:
            csv.writer(file).writerow(field_names)

    urls = []
    with open(f'../scraping_results/{input_name}.csv', newline='') as f:
        reader = csv.reader(f)    
        for entry in reader:
            urls.append(entry[0])

    for url in tqdm(urls):
        response = session.get(url)
        try:
            result = page_scrapper(response.text, url)
            if isinstance(result, dict):
                with open(f'../scraping_results/{output_data_name}.csv', 'a', newline='') as file:
                    csv.DictWriter(file, fieldnames=field_names).writerow(result)
            elif isinstance(result, list):
                with open(f'../scraping_results/{output_url_name}.csv', 'a', newline='') as file:
                    for link in result:
                        csv.writer(file).writerow(link)
        except Exception as ex:
            with open(f'../scraping_results/{output_fail_name}.csv', 'a', newline='') as file:
                csv.writer(file).writerow([url, ex])                
            continue

url_scrapper(page_names, session, 'test_urls')
main_scrapper('test_urls', 'test_data', 'test_add_urls', 'test_fails', session)
main_scrapper('test_add_urls', 'test_data', 'test_add_urls_2', 'test_fails', session)

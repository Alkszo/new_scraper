import requests
from bs4 import BeautifulSoup as bs
import csv
import os
from tqdm import tqdm
from url_scrapper import url_scrapper
from page_scrapper import page_scrapper

page_names = []
with open('page_names.csv', newline='') as f:
    reader = csv.reader(f)    
    for entry in reader:
        page_names.append(entry[0])

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

#defining requests session
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
            result = page_scrapper(response.text)
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
            print(ex)    
            continue


#url_scrapper(page_names, session, 'urls')
main_scrapper('urls', 'property_data', 'additional_urls', 'failed_urls', session)
main_scrapper('additional_urls', 'property_data', 'additional_urls_2', 'failed_urls', session)

import re
import requests
from bs4 import BeautifulSoup as bs
import json
import csv
from tqdm import tqdm


def requests_scrapper(html_text, property_type=0):
    """
    A function which scraps properties from individual immowebpage. It takes html text as argument and returns False if listing is for life annuity, 
    a list of urls if the page contains references to a group of properties (developement project) or a dictionary containing property data
    """

    real_estate = {'immo_id': None, 'zip_code': None, 'type_of_property': property_type, 'subtype_of_property': None, 'price': None, 'building_condition': None, 'facade_number': None, 'living_area': None, 
               'equipped_kitchen': 0, 'bedroom_nr': None, 'swimming_pool': 0, 'furnished': 0, 'open_fire': 0, 'terrace': 0, 'garden': 0, 'plot_surface': 0}
    url_list = []

    soup = bs(html_text, 'html.parser')    

    #indentifies a json object with property data within page script, isolates it and converts to python dictionary
    info_script = soup.find('script', string=re.compile("window.dataLayer.push"))
    expr = re.compile('"classified":[\S\n ]+"customer":')   
    dict_like = re.findall(expr, info_script.string)[0]
    dict_like = re.sub('"classified":', '', dict_like)
    dict_like = re.sub(',\n\s*"customer":', '', dict_like)        
    prop_dict = (json.loads(dict_like))    

    #identifying page title and potential signs of life annuity sale
    annuitant_check = soup.find_all('th', string=re.compile("annuitant"))
    title = soup.find('title').text

    #if the listing is for life annuity funtion terminates and returns False
    if len(annuitant_check) > 0:
        return False

    #the titles of individual properties offers always contain a number of square meters of living area, 
    #this is used as indicator that the page doesn't conatain a bundle and functions proceeds to fill in the dictionary
    elif len(re.findall("(\s\d+m)", title)) > 0:
        real_estate['living_area'] = int(re.findall("(\s\d+m)", title)[0][1:-1])

        #info about the number of frontages is found in main body of html page in the table  
        frontages_header = soup.find("th", class_="classified-table__header", string=re.compile("Number of frontages"))
        if frontages_header is not None:
                real_estate['facade_number'] = int(frontages_header.parent.find('td').string.strip())

        #looks for information about terrace arean in the page body. If none is found but script lists terrace as existed the surface is set to 1
        terrace_header = soup.find("th", class_="classified-table__header", string=re.compile("Terrace surface"))
        if terrace_header is not None:
            data_cell = terrace_header.parent.find('td')
            real_estate['terrace'] = int(re.findall("(\d+)", str(data_cell))[0])

        #checks if the property is furnisehd and changes the dictionary binary if that's the case
        furnished_header = soup.find("th", class_="classified-table__header", string=re.compile("Furnished"))
        if furnished_header is not None:
            if furnished_header.parent.find('td').string.strip() == "Yes":
                real_estate['furnished'] = 1

        #grabs description element of the page and checks if there's an information about open fire
        descr = soup.find('p', class_="classified__description")
        if descr is not None:
            if 'open fire' in descr.text:
                real_estate['open_fire'] = 1

        #fills all the remaining dictionary values with json object properties recovered from page's script
        real_estate['zip_code'] = int(prop_dict['zip'])
        real_estate['immo_id'] = prop_dict['id']
        real_estate['subtype_of_property'] = prop_dict['subtype']
        if prop_dict['price'] == "no price":
            real_estate['price'] = None
        else:    
            real_estate['price'] = int(prop_dict['price'])
        real_estate['building_condition'] = prop_dict['building']['condition']    
        real_estate['bedroom_nr'] = int(prop_dict['bedroom']['count'])
        if prop_dict['kitchen']['type'] != "":
            real_estate['equipped_kitchen'] = prop_dict['kitchen']['type']
        if prop_dict['wellnessEquipment']['hasSwimmingPool'] == "true":
            real_estate['swimming_pool'] = 1
        if prop_dict['outdoor']['terrace']['exists'] == "true" and real_estate['terrace'] == 0:
            real_estate['terrace'] = 1
        if 'surface' in prop_dict['outdoor']['garden'] and prop_dict['outdoor']['garden']['surface'] != "":
            real_estate['garden'] = int(prop_dict['outdoor']['garden']['surface'])
        if prop_dict['land']['surface'] != "":
            real_estate['plot_surface'] = int(prop_dict['land']['surface'])

        return real_estate
    
    #if a page contains links to more sales the list urls is returned 
    elif "group" in prop_dict['type']:
        anchor = soup.find('template', string=re.compile("All properties"))
        for link in anchor.parent.find_all('a'):
            url_list.append([link['href']])
        
        return url_list
    
    #failsafe in case of getting irregularly structured page, avoids unnecessary errors
    else:
        return True
    

def scraping_session(property_type=0): #property_type is binary for is_house: 0=apartment, 1=house
    """
    a function that runs a loop on provided link list, the type of property house/appartment should be speccified
    """

    field_names = ['immo_id', 'zip_code', 'type_of_property', 'subtype_of_property', 'price', 'building_condition', 'facade_number', 'living_area', 'equipped_kitchen', 'bedroom_nr', 'swimming_pool', 'furnished', 'open_fire', 'terrace', 'garden', 'plot_surface']

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    #defining requests session
    session = requests.Session()
    session.headers = headers

    #defining paths for loading urls and saving results
    apartments_path = "url_store/apartments_links.csv"
    houses_path = "url_store/houses_links.csv"    
    apartments_save = "Alek_scrapper_results/apartment"
    houses_save = "Alek_scrapper_results/houses"

    #the scrapping loop proper, the list of links is fetched from appropriate file then the scrapping function runs through them
    #results are saved in appropriate files: data as final result, additional links for next round of scrapping and errors for testing and quality control
    def scraping_loop(load_path, save_path):

        csv_list = []
        with open(load_path, newline='') as f:
            reader = csv.reader(f)    
            for entry in reader:
                csv_list.append(entry[0])

        all_links = csv_list[1:]

        for link in tqdm(all_links):
            response = session.get(link, headers=headers)
            try:
                result = requests_scrapper(response.text, property_type)
                if isinstance(result, dict):
                    with open(f'{save_path}_data.csv', 'a', newline='') as file:
                        csv.DictWriter(file, fieldnames=field_names).writerow(result)
                elif isinstance(result, list):
                    with open(f'{save_path}_additional_urls.csv', 'a', newline='') as file:
                        for url in result:
                            csv.writer(file).writerow(url)
            except Exception as ex:
                with open(f'{save_path}_failed_urls.csv', 'a', newline='') as file:
                    csv.writer(file).writerow([link])        
                continue

    #check if the loop is to be run for houses or appartments
    if property_type == 1:
        scraping_loop(houses_path, houses_save)
    else:
        scraping_loop(apartments_path, apartments_save)

#at this point the program is set to run houses urls scrapping, it has to be re-run a couple of times in order to obtain full dataset
scraping_session(1)

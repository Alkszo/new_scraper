from bs4 import BeautifulSoup as bs
import re
import json


def page_scrapper(html_text, url):    
    """
    A function which scraps properties from individual immowebpage. It takes html text as argument and returns False if listing is for life annuity, 
    a list of urls if the page contains references to a group of properties (developement project) or a dictionary containing property data
    """

    soup = bs(html_text, "html.parser")

    info_script = soup.find('script', string=re.compile("av_items = \[\{"))
    expr = re.compile("av_items = \[\{[\S\n ]+\}\]")
    dict_like = re.findall(expr, info_script.string)[0]
    dict_like = re.sub('av_items = \[', '', dict_like)
    dict_like = re.sub('\]', '', dict_like)
    dict_like = re.sub('"list_name":.*,\n', '', dict_like)
    dict_like = re.sub(',\n.*\}', '}', dict_like)    
    prop_dict = (json.loads(dict_like))

    url_list = []
    real_estate = {'immo_id': None, 'zip_code': None, 'province':None, 'price': None, 'subtype_of_property': None, 'building_condition': None, 'living_area': None, 'year_of_construction': None, 
               'energy_certificate': None, 'geolocation': None, 'equipped_kitchen': None, 'bedroom_nr': None, 'swimming_pool': 0, 'terrace': 0, 'garden': 0, 'plot_surface': 0, 'url': url}

    annuitant_check = soup.find_all('th', string=re.compile("annuitant"))
    title = soup.find('title').text    

    if len(annuitant_check) > 0:
        return False
    
    elif len(re.findall("(\s\d+m)", title)) > 0:
        real_estate['immo_id'] = int(prop_dict['id'])
        real_estate['zip_code'] = int(prop_dict['zip_code'])
        real_estate['province'] = prop_dict['province']
        real_estate['price'] = int(prop_dict['price'])
        real_estate['subtype_of_property'] = prop_dict['subtype']
        real_estate['building_condition'] = prop_dict['building_state']
        real_estate['living_area'] = int(prop_dict['indoor_surface'])
        if prop_dict['year_of_construction'] != '':
            real_estate['year_of_construction'] = int(prop_dict['year_of_construction'])
        real_estate['energy_certificate'] = prop_dict['energy_certificate']
        real_estate['geolocation'] = prop_dict['geolocation']
        real_estate['equipped_kitchen'] = prop_dict['kitchen_type']
        real_estate['bedroom_nr'] = int(prop_dict['nb_bedrooms'])
        pool_indicator = re.findall('"wellnessEquipment": \{\n.*"hasSwimmingPool":.*"', info_script.string)[0][-5:-1]
        if pool_indicator == 'true':
            real_estate['swimming_pool'] = 1
        if prop_dict['outdoor_terrace_exists'] == 'true':
            real_estate['terrace'] = 1
        if prop_dict['outdoor_surface'] != '':
            real_estate['garden'] = int(prop_dict['outdoor_surface'])
        if prop_dict['land_surface'] != '':
            real_estate['plot_surface'] = int(prop_dict['land_surface'])

        return real_estate

    elif 'group' in prop_dict['subtype']:
        anchor = soup.find('template', string=re.compile("All properties"))
        for link in anchor.parent.find_all('a'):
            url_list.append([link['href']])
        
        return url_list
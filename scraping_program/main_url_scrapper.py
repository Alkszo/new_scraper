from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json

def bot_session(starting_point, property_type):
    """
    This function creates a selenium session and goes through the subpages of immoweb search results in order to get a list of links to property listings
    """

    #defines selenium session
    service = Service(executable_path="web_drivers/chromedriver_win.exe")
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(5)
    driver.get(starting_point)
    driver.maximize_window()

    #identify and close cookies popup window
    top_div = driver.find_element(By.ID, 'usercentrics-root')
    shadow_root = top_div.shadow_root
    confirm_button = shadow_root.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']")
    confirm_button.click()

    #identify the navigation element responsible for changin between pages
    ulist = driver.find_element(By.CLASS_NAME, "pagination")
    litems = ulist.find_elements(By.TAG_NAME, "li")
    pages_number = int(litems[-2].find_elements(By.TAG_NAME, "span")[1].text)
    
    url_list = []
    #loops through all the pages and grabs urls that direct to other immoweb listings (not advertisments or other property developer)
    for i in range(pages_number):        
        soup = bs(driver.page_source, 'html.parser')
        main_list = soup.find('ul', id='main-content')
        links = main_list.find_all('a')
        for link in links:
            url = link['href']
            if "immoweb.be" in url:
                url_list.append(url)        

        #chenges to next page if not on the last page of results
        if i < pages_number - 1:                        
            litems[-1].click()
            time.sleep(2) #wait for the next page to load

    #saving the url list into json file
    url_book = {'urls': url_list}
    url_book_json = json.dumps(url_book, indent=4)
    with open(f'url_store/{property_type}_all.json', 'w') as save_file:
        save_file.write(url_book_json)

bot_session("https://www.immoweb.be/en/search/apartment/for-sale", "apartments")
bot_session("https://www.immoweb.be/en/search/house/for-sale", "houses")
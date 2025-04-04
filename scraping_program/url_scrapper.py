from bs4 import BeautifulSoup as bs
import csv
import re
from tqdm import tqdm


def url_finder(url, session):
    """
    Function identifies links to property offers in the main body of Immoweb page. Returns a list of urls or False if the page contains no links.
    """

    response = session.get(url)
    soup = bs(response.text, "html.parser")

    #identifies main content of the page leaving out suggestions in the footer (avoid bloat and duplicates)
    h1 = soup.find("h1", string=re.compile("for sale"))
    parent = h1.find_parent("div").find_parent("div")
    links = parent.find_all("a", class_="card__title-link")

    if len(links) == 0:
        return False    
    else:
        url_list = []
        for link in links:
            url_list.append(link['href'])
        return url_list
    
    
def url_scrapper(page_list, session, output_name):
    """
    Function iterates over all localieties supplied in page_list and extracts offer urls from each search result page 
    """

    for page_name in tqdm(page_list):
        i = 1 #counter for search result pages
        result = url_finder(f'https://www.immoweb.be/en/search/house-and-apartment/for-sale/{page_name}?countries=BE&page={i}&orderBy=relevance', session)
        while result is not False:
            with open(f'../scraping_results/{output_name}.csv', 'a', newline='') as file:
                for url in result:
                    csv.writer(file).writerow([url]) #url put into list in order to be treated as singular csv entry, not list of chars

            i+=1        
            result = url_finder(f'https://www.immoweb.be/en/search/house-and-apartment/for-sale/{page_name}?countries=BE&page={i}&orderBy=relevance', session)
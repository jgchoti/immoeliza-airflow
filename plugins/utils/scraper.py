import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
from utils.cleaner import Cleaner
from utils.retriever import Retriever
from utils.output import Output
from utils.config import ALL_KEYS
import certifi
from http.client import RemoteDisconnected
from fake_useragent import UserAgent
from datetime import datetime
from zoneinfo import ZoneInfo
import cloudscraper


class Scraper:
    def __init__(self, category_type: str, page: int = 1, ):
        self.page = page
        self.category_type = category_type 
        self.output = Output(postgres_conn_id='postgres_default') 
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'firefox',
                'platform': 'linux',  
                'mobile': False
            },
            delay=10,
            debug=False
        )
        self.properties_data = {}
        self.page_urls = []
        self.seen_url = set()
        self.seen_zimmo_code = set()
        self.ua = UserAgent(platforms='desktop')
        self.headers = {
            'User-Agent': self.get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
            'Connection': 'keep-alive',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.zimmo.be'
        }
       
    def close(self):
        self.session.close()
        
    def get_user_agent(self):
        return self.ua.random
        
    def open_page(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = self.headers.copy()
                headers['User-Agent'] = self.get_user_agent()
                
                time.sleep(random.uniform(2, 5))
                
                response = self.session.get(
                    url, 
                    headers=headers,
                    timeout=30,
                    allow_redirects=True,
                    stream=False
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return soup
                elif response.status_code == 403:
                    print(f"🚫 403 Forbidden on attempt {attempt + 1} for {url}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(5, 10))
                        continue
                else:
                    print(f"❌ HTTP {response.status_code} for {url}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(3, 6))
                        continue
                        
            except (RemoteDisconnected, requests.exceptions.RequestException) as e:
                print(f"🔌 Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))
                    continue
                    
        print(f"❌ Failed to reach {url} after {max_retries} attempts")
        return False
     
    def update_page_number(self, page_number, url):
        if page_number == 1:
            return url
        else:
            return f"{url}&p={page_number}"
        
    def get_links(self, soup):
        properties_url = []
        properties = soup.find_all("div", class_="property-item")
        for listing in properties:
            a_elem = listing.find("a", href=True)
            if a_elem and a_elem.get('href'):
                properties_url.append(a_elem['href'])
        return properties_url
    
    def scrape_property(self, link):
        full_link = urljoin("https://www.zimmo.be", link)
        if full_link in self.seen_url:
            print(f"❌ Skipped {full_link} ")
            return
        
        self.seen_url.add(full_link)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = self.headers.copy()
                headers['User-Agent'] = self.get_user_agent()
                headers['Referer'] = 'https://www.zimmo.be/'
                
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(
                    full_link, 
                    headers=headers, 
                    verify=certifi.where(),
                    timeout=30,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 403:
                    print(f"🚫 403 Forbidden on attempt {attempt + 1} for {full_link}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(5, 10))
                        continue
                else:
                    print(f"{response.status_code} : ❌ Failed to fetch {full_link}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(3, 6))
                        continue
                        
            except (RemoteDisconnected, requests.exceptions.RequestException) as e:
                print(f"🔌 Connection error on attempt {attempt + 1} for {full_link}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))
                    continue
        
        print(f"❌ Failed to fetch {full_link} after {max_retries} attempts")
        return None
    
    def process_soup(self, raw_html, link):
        full_link = urljoin("https://www.zimmo.be", link)
        if raw_html is None:
            print(f"No HTML content received from {full_link}")
            return None
        
        soup = BeautifulSoup(raw_html, "html.parser")
        retrieve = Retriever(soup)
        
        # get zimmo code
        zimmo_code = retrieve.get_zimmo_code()
        if not zimmo_code:
            print(f"⚠️ Skipped property with missing zimmo_code: {retrieve.url}")
            return
        cleaned_zimmo_code = Cleaner.clean_zimmo_code(zimmo_code) if zimmo_code else None
        if self.output.exists(cleaned_zimmo_code):
            print(f"⚠️ Skipping {cleaned_zimmo_code}: already in DB")
            return None

        if cleaned_zimmo_code in self.seen_zimmo_code:
            print(f"❌ Skipped duplicated Zimmo-Code in current run: {cleaned_zimmo_code}")
            return

        self.seen_zimmo_code.add(cleaned_zimmo_code)

        feature = retrieve.get_feature_info()
        feature["prijs"] = Cleaner.cleaned_price(feature["prijs"]) if feature.get("prijs") else None
        address = Cleaner.clean_address(feature.get("adres")) if feature.get("adres") else {}
        feature["woonopp."] = Cleaner.remove_non_digits(feature["woonopp."]) if feature.get("woonopp.") else None
        feature["grondopp."] = Cleaner.remove_non_digits(feature["grondopp."]) if feature.get("grondopp.") else None
        feature["epc"]  = Cleaner.remove_non_digits(feature["epc"]) if feature.get("epc") else None
        feature['renovatieplicht'] = Cleaner.cleaned_renovation_obligation(feature['renovatieplicht']) if feature.get('renovatieplicht') else None
        feature['ki'] = Cleaner.cleaned_price(feature['ki']) if feature.get('ki') else None
        feature['bouwjaar'] = Cleaner.clean_year(feature['bouwjaar']) if feature.get('bouwjaar') else None
        
        mobiscore = retrieve.get_mobiscore() 


        scraped_sub_type = feature.get("type")

        data = {
            "zimmo_code": zimmo_code,
            "type": self.category_type,  
            "sub_type": scraped_sub_type, 
            "price": feature.get("prijs"),
            "street": address.get("street") if isinstance(address, dict) else None,
            "number": address.get("number") if isinstance(address, dict) else None,
            "postcode": address.get("postcode") if isinstance(address, dict) else None,
            "city": address.get("city") if isinstance(address, dict) else None,
            "living_area_m2": feature.get("woonopp."),
            "ground_area_m2": feature.get("grondopp."),
            "bedroom": feature.get("slaapkamers"),
            "bathroom": feature.get("badkamers"),
            "garage": feature.get("garages"),
            "garden": True if feature.get("tuin") else False,
            "epc_kwh_m2": feature.get("epc"),
            "renovation_obligation": feature.get("renovatieplicht"),
            "year_built" : feature.get('bouwjaar'),
            "mobiscore" : mobiscore, 
            "url": full_link,
            "scraped_at": datetime.now(ZoneInfo("Europe/Brussels")).isoformat()
        }
        
        
        for key in ALL_KEYS:
            data.setdefault(key, None)
        
        data = Cleaner.cleaned_data(data)
        print(data)
        return cleaned_zimmo_code, data
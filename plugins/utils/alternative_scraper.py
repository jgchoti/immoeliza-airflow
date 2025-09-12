import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
from datetime import datetime
from zoneinfo import ZoneInfo

class AlternativeScraper:
    def __init__(self, category_type="HOUSE"):
        self.category_type = category_type.upper()
        self.session = requests.Session()
        self.ua = UserAgent(platforms='desktop')
        self.headers = {
            'User-Agent': self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            'Connection': 'keep-alive'
        }

    def get_sample_data(self):
        print("Generating sample for testing...")

        now = datetime.now(ZoneInfo("Europe/Brussels")).isoformat()
        sample_properties = [
            {
                "zimmo_code": "SAMPLE001",
                "type": "HOUSE",
                "sub_type": None,
                "price": 350000,
                "street": "Sample Street",
                "number": "123",
                "postcode": "1000",
                "city": "Brussels",
                "living_area_m2": 120,
                "ground_area_m2": 300,
                "bedroom": 3,
                "bathroom": 2,
                "garage": 1,
                "garden": True,
                "epc_kwh_m2": 150,
                "renovation_obligation": False,
                "year_built": 2010,
                "mobiscore": 75,
                "url": "https://example.com/property1",
                "scraped_at": now
            },
            {
                "zimmo_code": "SAMPLE002",
                "type": "APARTMENT",
                "sub_type": None,
                "price": 250000,
                "street": "Test Avenue",
                "number": "456",
                "postcode": "2000",
                "city": "Antwerp",
                "living_area_m2": 85,
                "ground_area_m2": None,
                "bedroom": 2,
                "bathroom": 1,
                "garage": 0,
                "garden": False,
                "epc_kwh_m2": 120,
                "renovation_obligation": True,
                "year_built": 1995,
                "mobiscore": 80,
                "url": "https://example.com/property2",
                "scraped_at": now
            },
            {
                "zimmo_code": "SAMPLE003",
                "type": "HOUSE",
                "sub_type": None,
                "price": 450000,
                "street": "Demo Road",
                "number": "789",
                "postcode": "3000",
                "city": "Ghent",
                "living_area_m2": 150,
                "ground_area_m2": 500,
                "bedroom": 4,
                "bathroom": 3,
                "garage": 2,
                "garden": True,
                "epc_kwh_m2": 100,
                "renovation_obligation": False,
                "year_built": 2015,
                "mobiscore": 85,
                "url": "https://example.com/property3",
                "scraped_at": now
            }
        ]

        print(f"✅ Generated {len(sample_properties)} sample properties")
        return sample_properties

    def scrape_all_price_ranges(self):
        print(f"🏠 Simulating scraping for category: {self.category_type}")

        all_data = self.get_sample_data()
        filtered_data = [prop for prop in all_data if prop["type"].upper() == self.category_type]

        print(f"📊 Found {len(filtered_data)} properties for {self.category_type}")

        result = {prop["zimmo_code"]: prop for prop in filtered_data}
        return result

    def cleanup(self):
        self.session.close()
        print("Alternative scraper cleanup completed")

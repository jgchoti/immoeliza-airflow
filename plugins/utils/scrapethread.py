import threading
from utils.scraper import Scraper
import pandas as pd
class ScrapeThread(threading.Thread):
    def __init__(self, url, results, lock, category_type):
        super().__init__()
        self.url = url
        self.results = results
        self.lock = lock
        self.category_type = category_type

    def run(self):
        scraper = Scraper(self.category_type)
        try:
            raw_html = scraper.scrape_property(self.url)
            results = scraper.process_soup(raw_html, self.url)
            if results is not None:
                zimmo_code, data = results
                if zimmo_code and data:
                    data["type"] = self.category_type
                    with self.lock:
                        self.results[zimmo_code] = data
        finally:
            scraper.close()


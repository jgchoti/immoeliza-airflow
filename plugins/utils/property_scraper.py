import threading
import time
from datetime import datetime
from utils.scraper import Scraper
from utils.scrapethread import ScrapeThread
from utils.output import Output
from utils.url_generator import URLgenerator
from utils.alternative_scraper import AlternativeScraper    
import os

class PropertyScraper:
    def __init__(self, category_type, max_workers=None, db_uri=None ):
        self.max_workers = 2
        self.max_price_ranges = 50
        self.max_pages_per_range = 100
        self.db_uri = db_uri
        self.scraper = None
        self.output = None
        self.results_lock = threading.Lock()
        self.base_url = {}
        self.category_type = category_type
        
    
    def get_base_url(self):
        url_generator = URLgenerator(category_type=self.category_type)
        urls_dict = url_generator.generate_url_with_price(0, 1400000, 50000)
        limited_items = list(urls_dict.items())[: self.max_price_ranges]
        self.base_url = dict(limited_items)

        
    def get_properties_each_page(self, properties_url):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = {}

        def run_one(url):
            t = ScrapeThread(url, results, self.results_lock, self.category_type)
            t.start()
            t.join()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(run_one, url) for url in properties_url]
            for _ in as_completed(futures):
                pass
        return results
    
    def scrape_price_range(self, key, url, first_write=True):
        self.setup()
        page = 1
        total_properties = 0
        
        while True:
            current_url = self.scraper.update_page_number(page, url)
            soup = self.scraper.open_page(current_url)
            
            if not soup:
                print(f"⚠️ Could not open page {page} for price range: {key}")
                break
                
            properties_url = self.scraper.get_links(soup)
            
            if not properties_url:
                print(f"🏷️ Done scraping listings in price range: {key}")
                break
                
            results = self.get_properties_each_page(properties_url)
            
            if results:
                self.output.save_to_db(results)
                first_write = False
                self.scraper.properties_data.update(results)
                total_properties += len(results)
                
            print(f"🔎 Done scraping listings in price range: {key} - Page: {page}")
            print(f"🗃️ Properties scraped this range: {total_properties}")
            print(f"🗃️ Total properties scraped so far: {len(self.scraper.properties_data)}")
            
            page += 1
            if page > self.max_pages_per_range:
                print(f"🔚 Reached max pages per range ({self.max_pages_per_range}) for {key}")
                break
            
        return first_write, total_properties
    
    def scrape_all_price_ranges(self, filename=None):

        self.setup()

        start_time = time.perf_counter()
        first_write = True
        summary = {
            'category_type': self.category_type,
            'total_properties': 0,
            'price_ranges_scraped': 0,
            'start_time': start_time,
            'price_range_results': {}
        }
        
        self.get_base_url()
        
        try:
            for key, url in self.base_url.items():
                print(f"\n🚀 Scraping {self.category_type}: Starting price range: {key}")
                first_write, properties_count = self.scrape_price_range(
                    key, url, first_write
                )
                
                summary['price_range_results'][key] = properties_count
                summary['total_properties'] += properties_count
                summary['price_ranges_scraped'] += 1
            
            if summary['total_properties'] == 0:
                print("⚠️  No properties found from zimmo.be, triggering fallback...")
                raise Exception("No properties found from zimmo.be")
                
        except Exception as e:
            print(f"❌ Error during zimmo.be scraping: {str(e)}")
            print("🔄 Falling back to alternative scraper with sample data...")
            
            alt_scraper = AlternativeScraper(category_type=self.category_type)
            try:
                property_data = alt_scraper.scrape_all_price_ranges()
                print(f"✅ Alternative scraper provided {len(property_data)} sample properties")

                if property_data:
                    try:
                        self.output.save_to_db(property_data, table_name='zimmo_data_sample')
                        summary['total_properties'] = len(property_data)
                        summary['price_ranges_scraped'] = 1
                        summary['price_range_results']['sample_data'] = len(property_data)
                        print(f"💾 Saved {len(property_data)} sample properties to database table 'zimmo_data_sample'")
                    except Exception as db_error:
                        print(f"⚠️  Database save failed (likely duplicates): {db_error}")
                
            finally:
                alt_scraper.cleanup()
            
        finally:
            end_time = time.perf_counter()
            summary['end_time'] = end_time
            summary['duration'] = end_time - start_time
            try:
                self.output.save_summary_to_db(summary)
            except Exception as summary_error:
                print(f"⚠️ Failed to save summary: {summary_error}")
            return summary
        
    
    def setup(self):
        from utils.scraper import Scraper
        from utils.output import Output
    
        self.scraper = Scraper(self.category_type)
        self.output = Output(postgres_conn_id='postgres_default')
            
    def cleanup(self):
        if self.scraper:
            self.scraper.close()
            
    def get_summary_report(self, summary):
        report = f"""
═══════════════ SCRAPING SUMMARY ═══════════════
🏠 Total Properties: {summary['total_properties']}
📊 Price Ranges Scraped: {summary['price_ranges_scraped']}
⏱️ Duration: {summary['duration']:.2f} seconds

📈 Results by Price Range:
"""
        for price_range, count in summary['price_range_results'].items():
            report += f"  • {price_range}: {count} properties\n"
            
        report += "=" * 30
        return report
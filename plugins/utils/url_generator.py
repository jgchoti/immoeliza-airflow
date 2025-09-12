import base64
import json
import threading
import logging

class URLgenerator:
    def __init__(self, category_type):
        self.category_type = category_type

    def generate_zimmo_url(self, min_price, max_price=None):
        query = {
            "filter": {
                "status": {"in": ["FOR_SALE", "TAKE_OVER"]},
                "category": {"in": [self.category_type]},
                "price": {
                    "unknown": False,
                    "range": {"min": min_price}
                }
            }
        }

        if max_price is not None:
            query["filter"]["price"]["range"]["max"] = max_price

        json_query = json.dumps(query, separators=(',', ':'))
        encoded_query = base64.b64encode(json_query.encode()).decode()
        return f"https://www.zimmo.be/nl/zoeken/?search={encoded_query}"

    def generate_price_ranges_with_open_end(self, start, max_limit, step):
        current = start
        while current + step - 1 <= max_limit:
            yield (current, current + step - 1)
            current += step
        yield (max_limit + 1, None)

    def generate_url_with_price(self, start, max_limit, step):
        urls = {}
        for min_p, max_p in self.generate_price_ranges_with_open_end(start, max_limit, step):
            url = self.generate_zimmo_url(min_p, max_p)
            urls[f"{min_p} - {max_p if max_p is not None else 'no max'}"] = url
            logging.info(f"{min_p} - {max_p if max_p is not None else 'no max'}: {url}")
        return urls

# # Test the fixes
# if __name__ == "__main__":
#     generator = URLgenerator("HOUSE")
    
#     # Test with small range for debugging
#     print("=== Testing small range ===")
#     urls = generator.generate_url_with_price(300000, 499999, 50000)
    
#     print(f"\nGenerated {len(urls)} URLs")
    
#     # Verify they're different by decoding a couple
#     url_list = list(urls.values())
#     if len(url_list) >= 2:
#         print("\n=== Verifying URLs are different ===")
#         for i, url in enumerate(url_list[:2]):
#             search_param = url.split("search=")[1]
#             decoded = base64.b64decode(search_param).decode()
#             print(f"URL {i+1} decoded: {decoded}")
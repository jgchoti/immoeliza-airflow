from utils.property_scraper import PropertyScraper

def main():

    print("\n🔍 Getting data...")
    scraper = PropertyScraper()
    try:
        categories = ["HOUSE", "APARTMENT"]
        filenames = []

        for category in categories:
            filename = f"properties_{category.lower()}.csv"
            summary = scraper.scrape_all_price_ranges(category_type=category, filename=filename)
            print(scraper.get_summary_report(summary))
            filenames.append(filename)

        user_input = input("\n📖 Do you want to preview results? ('y' to confirm): ")
        if user_input.lower() == "y":
            for fname in filenames:
                scraper.output.read_csv(fname)
                scraper.output.output_info(fname)
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    main()

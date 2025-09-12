import re

class Cleaner:
    @staticmethod
    def clean_address(full_address):
        cleaned = re.sub(r"\n+|\s+", " ", full_address).strip()
        street_part, city_part = cleaned.split(",", 1)
        street_parts = street_part.strip().split()
        street_name_parts = []
        number_parts = []
        for i, part in enumerate(street_parts):
            if re.search(r"\d", part):
                street_name_parts = street_parts[:i]
                number_parts = street_parts[i:]
                break
            else:
                street_name_parts = street_parts
                number_parts = []

        street_name = " ".join(street_name_parts).strip() if street_name_parts else None
        number = " ".join(number_parts).strip() if number_parts else None
        if number is not None:
            number = re.sub(r"\s", "", number)
        postcode, city = city_part.strip().split(" ", 1)
        if street_name == "Straat niet gekend":
            street_name = None
        return {
            "street": street_name,
            "number": number,
            "postcode": postcode,
            "city": city,
        }

    @staticmethod
    def clean_zimmo_code(code):
        cleaned = code.replace(r"Zimmo-code: ", "").strip()
        cleaned = re.sub(r"\s", "", cleaned)
        return cleaned

    @staticmethod
    def clean_text(text):
        cleaned = text.strip()
        return cleaned
    
    @staticmethod
    def remove_non_digits(text):
        period_count = text.count('.')
        comma_count = text.count(',')
        if period_count > 0 and comma_count > 0:
            cleaned = text.replace(".", "")
            cleaned = cleaned.replace(",", ".")
        elif comma_count > 1:
            cleaned = text.replace(",", "")
        elif period_count > 1:
            cleaned = text.replace(".", "")
        elif comma_count == 1 and text.rfind(',') > text.rfind('.'):
            cleaned = text.replace(",", ".")
        else:
            cleaned = text.replace(",", "")
        cleaned = re.sub(r"[^0-9.]", "", cleaned)
        if cleaned == "":
            return None
        return float(cleaned)

    @staticmethod
    def cleaned_price(price):
        cleaned = re.sub(r"[€\s]", "", price)
        cleaned = cleaned.replace(".", "")
        cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def cleaned_renovation_obligation(text):
        return text.strip().lower() == "van toepassing"

    @staticmethod
    def cleaned_data(data):
        for key, value in data.items():
            if isinstance(value, str) and "op aanvraag »" in value:
                data[key] = None
        return data 
    
    @staticmethod
    def clean_year(year_value):
        if not year_value:
            return None

        cleaned_digits = re.sub(r"[^0-9]", "", str(year_value))
        if cleaned_digits:
            try:
                return int(cleaned_digits)
            except (ValueError, TypeError):
                return None
        return None
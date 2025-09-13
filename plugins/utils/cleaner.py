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
    
    import re

    @staticmethod
    def remove_non_digits(text):
        if not text:
            return None
        
        text = text.strip()
        if not text:
            return None
 
        text = re.sub(
        r'(?i)\s*(m2|m²|sqm|sq\s*m|sq\.?\s*m|square\s+meters?|square\s+metres?|'
        r'kwh/m2|kwh/m²|kwh\s+per\s+m2|kwh\s+per\s+m²)\b',
        '',
        text
        )
    
        match = re.search(r'[-+]?\d[\d\.,]*', text)
        if not match:
            return None
        
        num_str = match.group(0)
    
        # Count separators
        dot_count = num_str.count('.')
        comma_count = num_str.count(',')
    
        # Handle mixed separators (dot and comma)
        if dot_count > 0 and comma_count > 0:
        # Determine which is decimal separator based on position
            last_comma_pos = num_str.rfind(',')
            last_dot_pos = num_str.rfind('.')
        
            if last_comma_pos > last_dot_pos:
            # Comma is decimal separator: 1.234,56
                num_str = num_str.replace('.', '').replace(',', '.')
            else:
                # Dot is decimal separator: 1,234.56
                num_str = num_str.replace(',', '')
    
        # Handle comma-only formatting
        elif comma_count > 0 and dot_count == 0:
            if comma_count > 1:
                # Multiple commas = thousand separators: 1,234,567
                num_str = num_str.replace(',', '')
            else:
                # Single comma - determine if thousand separator or decimal
                parts = num_str.split(',')
                if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit():
                    # Thousand separator: 1,234
                    num_str = num_str.replace(',', '')
                else:
                    # Decimal separator: 1,25
                    num_str = num_str.replace(',', '.')
    
        # Handle dot-only formatting
        elif dot_count > 0 and comma_count == 0:
            if dot_count > 1:
                # Multiple dots = thousand separators: 1.234.567
                num_str = num_str.replace('.', '')
            else:
                # Single dot - determine if thousand separator or decimal
                parts = num_str.split('.')
                if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit():
                    # Likely thousand separator: 1.234
                    num_str = num_str.replace('.', '')
                # Otherwise keep as decimal separator
    
        # Clean up any remaining non-numeric characters except decimal point
        num_str = re.sub(r'[^0-9.-]', '', num_str)
    
        # Validate the result
        if not num_str or num_str in ['.', '-', '-.']:
            return None
    
        # Handle multiple decimal points that might remain
        if num_str.count('.') > 1:
            return None
    
        try:
            value = float(num_str)
            # Return integer if the value is a whole number
            return int(value) if value.is_integer() else value
        except ValueError:
            return None



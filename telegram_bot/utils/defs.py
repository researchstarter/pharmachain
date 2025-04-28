from datetime import datetime


def extract_batch_id_from_barcode(barcode_digits: str) -> int:
    """
    Extracts the original batch ID from a scanned barcode string.
    
    Steps:
    - Remove the last checksum digit
    - Remove any leading zeros
    - Convert to integer
    """
    if len(barcode_digits) < 2:
        raise ValueError("Barcode digits string too short.")
    
    # Remove the last checksum digit
    data_part = barcode_digits[:-1]
    
    # Remove leading zeros and convert to integer
    batch_id = int(data_part.lstrip('0'))
    
    return batch_id

# Timestampni sanaga o'zgartiruvchi funksiya
def timestamp_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')

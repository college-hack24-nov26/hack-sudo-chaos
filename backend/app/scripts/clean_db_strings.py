import re
from app.db.session import SessionLocal
from app.models.product import Product

def clean_string(s: str) -> str:
    if not s:
        return s
    # Strip registered/trademark symbols and non-breaking spaces
    s = s.replace('\xa0', ' ').replace(chr(160), ' ')
    s = s.replace(chr(174), '').replace('®', '').replace('™', '').replace('\ufffd', '')
    # Fix common accented characters that appear mangled
    s = s.replace('Crme', 'Creme').replace('crme', 'creme').replace('Crème', 'Creme')
    s = s.replace('', '')
    # Normalize spaces
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_brand(b: str) -> str:
    if not b:
        return b
    b = clean_string(b)
    brand_map = {
        'cadbery': 'Cadbury',
        'cadbery bornvita': 'Cadbury Bournvita',
        'bornvita': 'Bournvita',
        'bouenvita': 'Bournvita',
        'parle': 'Parle',
        'britannia': 'Britannia',
        'nestle': 'Nestle',
        'haldiram': "Haldiram's",
        "haldiram's": "Haldiram's",
        'itc': 'ITC',
        'sunfeast': 'Sunfeast',
        'amul': 'Amul',
        'dabur': 'Dabur',
        'tata': 'Tata',
        'marico': 'Marico',
    }
    b_lower = b.lower()
    return brand_map.get(b_lower, b.title())

def run_cleanup():
    with SessionLocal() as db:
        prods = db.query(Product).all()
        updated = 0
        for p in prods:
            old_name = p.product_name
            old_brand = p.brand_name
            new_name = clean_string(old_name)
            new_brand = clean_brand(old_brand) if old_brand else None
            
            # If name became 'HIDE & SEEK', make it friendly
            if new_name == 'HIDE & SEEK':
                new_name = 'Parle Hide & Seek Chocolate Chip Biscuits'
            elif new_name == 'Parle G':
                new_name = 'Parle-G Original Glucose Biscuits'

            if new_name != old_name or new_brand != old_brand:
                p.product_name = new_name
                p.brand_name = new_brand
                updated += 1

        db.commit()
        print(f"Successfully cleaned {updated} product names and brands in database.")

if __name__ == '__main__':
    run_cleanup()


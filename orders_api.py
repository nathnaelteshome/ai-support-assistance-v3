import requests
from config import FAKE_STORE_URL, DUMMY_JSON_URL

def get_order(order_id: int) -> dict:
    try:
        r = requests.get(f"{DUMMY_JSON_URL}/carts/{order_id}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Add fake status for demo
            data["status"] = "Shipped" if data["id"] % 2 == 0 else "Processing"
            return data
    except requests.RequestException:
        pass
    return None

def get_product(product_id: int) -> dict:
    try:
        r = requests.get(f"{FAKE_STORE_URL}/products/{product_id}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None

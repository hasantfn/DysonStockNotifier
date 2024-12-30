import requests
import json
from bs4 import BeautifulSoup


url = "https://www.dyson.com.tr/products/wet-dry-vacuums/dyson-v15-detect-submarine/overview/dyson-v15s-detect-submarine-sari-nikel"


def check_availability(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tüm script taglarını kontrol et
        script_tags = soup.find_all("script")
        for script in script_tags:
            if "Magento_Catalog/js/product/view/provider" in script.text:
                json_start = script.text.find('{')  # JSON başlangıç
                json_end = script.text.rfind('}') + 1  # JSON bitiş
                json_data = script.text[json_start:json_end]
                
                try:
                    # JSON'u ayrıştır
                    data = json.loads(json_data)

                    # Tek ürünün ID'sini al (keys() ile)
                    product_id = next(iter(data["*"]["Magento_Catalog/js/product/view/provider"]["data"]["items"].keys()))

                    # is_available kontrolü yap
                    is_available = data["*"]["Magento_Catalog/js/product/view/provider"]["data"]["items"][product_id]["is_available"]

                    # Sonucu yazdır
                    print(f"Product ID: {product_id}")
                    print(f"Product is available: {is_available}")
                    return is_available
                except (json.JSONDecodeError, KeyError) as e:
                    print("Error parsing JSON or finding 'is_available':", e)
                    return None
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None

# Örnek kullanım

check_availability(url)

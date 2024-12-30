from bs4 import BeautifulSoup
import requests

url = "https://www.dyson.com.tr/airwrap-id-multi-styler-dryer-straight-wavy-vinca-blue-topaz"
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
            print("JSON Data:", json_data)  # JSON'u yazdır
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")

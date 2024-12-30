import requests
from bs4 import BeautifulSoup

# URL of the page
url = "https://www.dyson.com.tr/airwrap-id-multi-styler-dryer-straight-wavy-vinca-blue-topaz"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # parse 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # CSS selector
    element = soup.select_one("body > div.page > footer > div.footer > div.footer-wrapper-sec > div > div.footer-block > div:nth-child(3) > div > ul > li:nth-child(10) > a")
    
    if element:
        print("Extracted text:", element.text.strip())
    else:
        print("Element not found")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")

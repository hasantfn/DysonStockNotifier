from bs4 import BeautifulSoup
import requests

url = "https://www.dyson.com.tr/airwrap-id-multi-styler-dryer-straight-wavy-vinca-blue-topaz"
response = requests.get(url)
html_content = response.text

# Step 2: Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Step 3: Extract data

add_to_cart = soup.select_one('#product_addtocart_form > div > div > div.card__action.product__action > div > div > a')
if add_to_cart:
    print("Add to Cart Button Text:", add_to_cart.text)
else:
    print("Add to Cart Button Not Found")




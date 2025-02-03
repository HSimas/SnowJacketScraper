import requests
from bs4 import BeautifulSoup
import time
import os

# Function to scrape Blue Tomato for men's snowboard jackets
def scrape_blue_tomato():
    base_url = 'https://www.blue-tomato.com/en-PT/products/categories/Snowboard+Shop-00000000--Snowboard+Clothing-00008Q20--Snowboard+Jackets-0000004Q/gender/men/'
    page = 1
    jackets = []
    brands = ['Burton', 'Volcom', '686', 'Quiksilver']

    while True:
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        items = soup.find_all('a', class_='_2RJQqQNZlsRvbio3VYmB Tj0DmqDsPrNoWvUEhuNj YNvXZqRqRfjoUPnwbbuD')
        if not items:
            break

        for item in items:
            brand = item.find('p', class_='M1fl8Y2Zv0ait8CyZlu2').text.strip()
            if brand in brands:
                title = item.find('p', class_='NEZ7QOkgPhytm2Ux6jHT').text.strip()
                if item.find('span', class_='WqIKE9a0T7O9ITTcb4s7 uinB_IBt7MnNG_lrlZok'):
                    price_original = (item.find('span', class_='WqIKE9a0T7O9ITTcb4s7 uinB_IBt7MnNG_lrlZok').text.strip()).replace('€\xa0', '€')
                    price_discount = (item.find('span', class_='WqIKE9a0T7O9ITTcb4s7 p0C_Amyq8hHAxpsbgdMI').text.strip()).replace('€\xa0', '€')
                else:
                    price_original = (item.find('span', class_='WqIKE9a0T7O9ITTcb4s7').text.strip()).replace('€\xa0', '€')
                    price_discount = '€0'
                link = f"https://www.blue-tomato.com{item['href']}"
                image_url = item.find('img')['src']
                jackets.append((brand, title, price_discount, price_original, link, image_url))

        page += 1

    return jackets

# Function to read previously saved jackets from text files
def read_previous_jackets():
    previous_jackets = {}
    for filename in os.listdir():
        if filename.startswith('snowboard_jackets') and filename.endswith('.txt'):
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(' - €')
                    link = parts[1].split(' ')[2].strip()
                    image_url = parts[1].split(' ')[3].strip()
                    price = parts[1].split(' ')[0].strip()
                    previous_jackets[link] = price
    return previous_jackets

# Function to save new jackets to a text file
def save_to_file(new_jackets):
    with open(f'snowboard_jackets{time.strftime("%Y%m%d-%H%M%S")}.txt', 'w', encoding='utf-8') as file:
        for jacket in new_jackets:
            file.write(jacket + '\n')

# Function to send new jackets to a Telegram group
def send_to_telegram(new_jackets, bot_token, chat_id):
    for jacket in new_jackets:
        brand, title, price, discount, link, image_url = jacket
        message = f"{brand} {title} - €{price} {discount}%: {link}"
        
        # Send the image with the caption
        image_payload = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": message,
            "parse_mode": "HTML"
        }
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendPhoto", data=image_payload)

# Main function
def main():
    # Replace with your bot token and chat ID
    bot_token = "7106870052:AAEPdaloTEz905qsCc0YfiGdS6smtQ7zIO4"
    chat_id = "7916310236"

    jackets = scrape_blue_tomato()
    previous_jackets = read_previous_jackets()
    new_jackets = []

    for jacket in jackets:
        brand, title, price_discount, price_original, link, image_url = jacket
        price_discount_value = float(price_discount.replace('€', ' '))
        price_original_value = float(price_original.replace('€', ' '))
        
        # Choose the lowest price between price_discount and price_original
        if price_discount_value == 0:
            lowest_price = price_original_value
            discount = 0
        else:
            lowest_price = price_discount_value
            discount = int((1 - (price_discount_value / price_original_value)) * 100)
        
        if link not in previous_jackets or lowest_price < float(previous_jackets[link].replace('€', '')):
            new_jackets.append((brand, title, lowest_price, discount, link, image_url))
    
    # Sort the new jackets by the lowest price
    new_jackets.sort(key=lambda x: x[2])
    
    # Format the output and save to file
    formatted_jackets = [f"{brand} {title.ljust(50)} - €{price:.2f} {discount}%: {link} {image_url}" for brand, title, price, discount, link, image_url in new_jackets]
    
    if formatted_jackets:
        save_to_file(formatted_jackets)
        send_to_telegram(new_jackets, bot_token, chat_id)
        print("Saved and sent to Telegram!")
    else:
        print("No new jackets!")

if __name__ == '__main__':
    main()

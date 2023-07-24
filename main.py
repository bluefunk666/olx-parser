import requests
from bs4 import BeautifulSoup
import tkinter as tk
import json

def parse_olx(category):
    url = f"https://www.olx.ua/{category}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Ошибка при получении данных. Проверьте URL и подключение к Интернету.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.find_all('tr', {'class': 'wrap'})
    if not items:
        print("Не удалось найти объявления в указанной категории.")
        return

    data = []
    for item in items:
        ad_id = item.get('data-id')
        image_links = [image.get('src') for image in item.find_all('img')]
        date_elem = item.find('td', {'class': 'bottom-cell'})
        if date_elem:
            date = date_elem.find('span').text.strip().split(',')[0]
        else:
            date = ""

        title = item.find('strong')
        if title:
            title = title.text.strip()

        price = item.find('p', {'class': 'price'})
        if price:
            price = price.text.strip()

        currency = item.find('strong', {'class': 'price_currency'})
        if currency:
            currency = currency.text.strip()

        description = item.find('td', {'valign': 'top'})
        if description:
            description = description.text.strip()

        owner = item.find('small', {'class': 'breadcrumb x-normal'})
        if owner:
            owner = owner.text.strip()

        phone = item.find('strong', {'class': 'big'})
        if phone:
            phone = phone.text.strip()

        location_elem = item.find('small', {'class': 'breadcrumb x-normal'})
        if location_elem:
            location = location_elem.text.strip().split(',')[0]
        else:
            location = ""

        region_elem = item.find('small', {'class': 'breadcrumb x-normal'}).find_next('span')
        if region_elem:
            region = region_elem.text.strip()
        else:
            region = ""

        characteristics = {}
        char_rows = item.find_all('tr', {'class': 'item'})
        for row in char_rows:
            key = row.find('span', {'class': 'charkey'})
            if key:
                key = key.text.strip()

            value = row.find('span', {'class': 'value'})
            if value:
                value = value.text.strip()

            if key and value:
                characteristics[key] = value

        item_data = {
            'ID': ad_id,
            'Фото': image_links[:10],
            'Дата объявления': date.replace('\n', ' '),
            'Название': title.replace('\n', ''),
            'Сумма': price.replace('\n', ''),
            'Валюта': currency,
            'Характеристики': characteristics,
            'Описание': description.replace('\n', ''),
            'Владелец': owner,
            'Телефон': phone,
            'Город': location.replace('\n', ''),
            'Область': region.replace('\n', '')
        }

        data.append(item_data)

    file_name = f"olx_data_{category}.json"
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print("Выгрузка данных успешно завершена.")

window = tk.Tk()
window.title("OLX Parser")

def parse_button_clicked():
    category = category_entry.get()
    if not category:
        print("Введите категорию.")
        return

    parse_olx(category)

category_label = tk.Label(window, text="Категория:")
category_label.pack()

category_entry = tk.Entry(window)
category_entry.pack()

parse_button = tk.Button(window, text="Выгрузить данные", command=parse_button_clicked)
parse_button.pack()

window.mainloop()
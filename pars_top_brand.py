import requests
from bs4 import BeautifulSoup
from time import sleep
import statistics
from fake_useragent import UserAgent


def parsing_top_brands(headers):
    top_brands = []

    pars_session = requests.Session()
    pars_session.headers.update(headers)

    # Получаем количество брендов в списке
    url = 'https://htreviews.org/tobaccos/brands?r=position&s=rating&d=desc'
    response = pars_session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    brands_count = soup.find('div', class_='tobacco_list_items').get('data-count')

    for count in range(0, 81, 20):  # Подгрузка элементов на страницу происходит кратно 20
        url = f"https://htreviews.org/getData?r=position&s=rating&d=desc&o={count}&action=brands"

        response = pars_session.get(url)

        if response:
            print(f"requests success, processing {brands_count} / {count} -> {count + 20}")

            response = response.json()
            for item in response:

                # рейтинг = оценка - (оценка / количество голосов)
                alt_rating = float(item['rating']) - (float(item['rating']) / float(item['ratings_count']))

                brand_item = [item['name'], item['rating'], alt_rating]
                top_brands.append(brand_item)

        else:
            print("[!] response error")

        if len(top_brands) >= int(brands_count):
            break

        sleep(2)

    # Сортируем список по вычисленному рейтингу
    top_brands = sorted(top_brands, key=lambda rating_sort: top_brands[2], reverse=True)

    statistics.save_list_to_csv('topBrands.csv', top_brands, True)
    print("--- parsing TOP BRANDS done! ---")


def main():
    fake_ua = UserAgent()
    headers = {"User-Agent": str(fake_ua.random)}
    parsing_top_brands(headers)


if __name__ == "__main__":
    main()

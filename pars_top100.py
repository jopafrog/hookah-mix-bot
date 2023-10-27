import requests
from time import sleep
import statistics
from fake_useragent import UserAgent

# b'Duebeck J\xc3\xa4germeister' utf-8


def parsing_top100(headers):
    top100 = []

    # Создаем сессию парсинга
    pars_session = requests.Session()
    pars_session.headers.update(headers)

    for count in range(0, 81, 20):
        url = f"https://htreviews.org/getData?r=position&s=rating&d=desc&o={count}&action=tobaccos"

        response = pars_session.get(url)

        if response:
            print(f"requests success, processing 100 / {count} -> {count + 20}")
            response = response.json()
            for item in response:

                if str(item['alt_name']) == 'None' or str(item['alt_name']) == '':
                    name = item['name']
                else:
                    name = item['alt_name']

                """рейтинг = оценка - (оценка / количество голосов)"""
                alt_rating = float(item['rating']) - (float(item['rating']) / float(item['ratings_count']))

                flavor = [name, item['brand'], item['rating'], alt_rating]
                top100.append(flavor)
        else:
            print("[!] response error")

        sleep(2)

    # Сортируем полученный список по вычисленному рейтингу
    top100 = sorted(top100, key=lambda rating_sort: rating_sort[3], reverse=True)

    statistics.save_list_to_csv('top100.csv', top100, True)
    print("--- parsing TOP100 done! ---")


def main():
    fake_ua = UserAgent()
    headers = {"User-Agent": str(fake_ua.random)}
    parsing_top100(headers)


if __name__ == "__main__":
    main()
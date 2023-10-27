import requests
from bs4 import BeautifulSoup
from time import sleep
import excelsave
from fake_useragent import UserAgent
from statistics import save_list_to_csv, update_flavors_list


def filter_name(name: str) -> str:
    if "кола" in name.lower() and name.lower() != "шоколад":
        name = "cola"

    elif "холодок" in name.lower():
        name = "холод"

    elif "мёд" in name.lower():
        name = "мед"

    return name


def all_flavors_list_get(headers) -> list:
    pars_flavors_list = []
    flavors_list_csv = []
    url = "https://htreviews.org/tobaccos"

    try:
        response = requests.get(url, headers=headers)

    except requests.ConnectionError:
        print(requests.ConnectionError)

    else:
        print("requests success, code:", response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')

        flavors_data = soup.find_all("div", class_="cs_value")

        for flavor in flavors_data:
            group = flavor.find("input", class_="cs_input").get("name")

            if str(group) == "t":
                name = flavor.find("div", class_="cs_input-text").text
                tag = flavor.find("input", class_="cs_input").get("value")
                #  print(name, tag)
                line = {"name": filter_name(name), "tag": tag}
                pars_flavors_list.append(line)

                row = [filter_name(name).lower(), tag, 0, 0]
                flavors_list_csv.append(row)

            else:
                break

    # save_list_to_csv('flavors.csv', flavors_list_csv, True, 'Название,тег,частота в миксах,спрос')
    update_flavors_list(flavors_list_csv)

    print("flavor list received")
    return pars_flavors_list


def parsing_flavor_top(flavor_name: str, tag: str) -> list:
    print("[INFO] Парсинг топа по вкусу -", flavor_name)
    top_flavor_list = []

    fake_ua = UserAgent()
    headers = {"User-Agent": str(fake_ua.random)}

    pars_session = requests.Session()
    pars_session.headers.update(headers)

    # Получаем количество табаков по нужному вкусу
    url = f'https://htreviews.org/tobaccos?r=flavor&s=rating&d=desc&t={tag}'
    response = pars_session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tobacco_count_data = soup.find('div', attrs={'class': 'tobacco_list_wrapper', 'data-type': 'flavor'})

    if tobacco_count_data is not None:
        tobacco_count = tobacco_count_data.find('div', class_='tobacco_list_items').get('data-count')

        for count in range(0, 81, 20):
            url = f"https://htreviews.org/getData?r=flavor&s=rating&d=desc&t={tag}&o={count}&action=tobaccos"

            try:
                response = pars_session.get(url)
            except requests.ConnectionError:
                print(requests.ConnectionError)

            if response:
                response = response.json()

                for item in response:
                    if float(item['ratings_count']) == 0:
                        alt_rating = 0
                    else:
                        # рейтинг = оценка - (оценка / количество голосов)
                        alt_rating = float(item['rating']) - (float(item['rating']) / float(item['ratings_count']))

                    line = {
                        "pos": item['key'], "name": item['name'], "alt_name": item['alt_name'],
                        "brand": item['brand'], "rating": item['rating'], "real_rating": alt_rating}

                    top_flavor_list.append(line)

                print(f"request success, processing {tobacco_count} / {count} -> {count + 20}")

            else:
                print("[ERR]", response.status_code, "count = ", count)
                break

            if len(top_flavor_list) >= int(tobacco_count):
                break

            sleep(2)

        # Сортируем полученный список по вычисленному рейтингу
        top_flavor_list = sorted(top_flavor_list, key=lambda rating_sort: rating_sort["real_rating"], reverse=True)

    else:
        print('Табаки со вкусом', flavor_name, 'отсутствуют')

    return top_flavor_list


def parsing_flavors(headers):
    flavors_list = all_flavors_list_get(headers)

    size = len(flavors_list)
    saved = 0
    all_flavors_sorting_top = []

    for flavor in flavors_list:
        top = parsing_flavor_top(flavor["name"], flavor["tag"])

        if len(top) != 0:
            page = {
                "flavor": flavor["name"].lower(), "data": top}
            all_flavors_sorting_top.append(page)
            saved += 1
            print(f"Прогресс: {(saved * 100) / size:.2f} %")

    excelsave.write_in_file(all_flavors_sorting_top)
    print("--- Parsing ALL FLAVORS done! ---")


def main():
    fake_ua = UserAgent()
    headers = {"User-Agent": str(fake_ua.random)}
    parsing_flavors(headers)


if __name__ == "__main__":
    main()

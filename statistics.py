import csv
from datetime import datetime
from dotenv import load_dotenv
from os import getenv


load_dotenv()
DIRECTORY = getenv("DIRECTORY")


def read_csv(file_name: str, title=False) -> list:
    flavors_book = []
    address = DIRECTORY + file_name
    with open(address, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        for row in reader:
            if title:
                title = False
                continue
            else:
                flavors_book.append(row)

    return flavors_book


def save_list_to_csv(file_name: str, saving_list: list, title=False, title_text=''):
    address = DIRECTORY + file_name
    with open(address, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # добавить запись с датой
        if title:
            title = [f"({title_text}) Parsing time: {str(datetime.today())}"]
            writer.writerow(title)

        for item in saving_list:
            writer.writerow(item)


def update_flavors_list(new_list: list):
    old_list = read_csv('flavors.csv', True)

    for new_id in range(0, len(new_list)):
        new_flavor = True
        for old_id in range(0, len(old_list)):
            if new_list[new_id][0] == old_list[old_id][0]:
                new_flavor = False
                break

        if new_flavor:
            old_list.append(new_list[new_id])

    save_list_to_csv('flavors.csv', old_list, True, 'Название,тег,частота в миксах,спрос')


def change_rating_in_flavors_list(item_name: str):
    all_items = read_csv('flavors.csv', True)

    for i in range(0, len(all_items)):
        if item_name in all_items[i]:
            all_items[i][len(all_items[i]) - 1] = int(all_items[i][len(all_items[i]) - 1]) + 1
            break

    save_list_to_csv('flavors.csv', all_items, True, 'Название,тег,частота в миксах,спрос')


def change_rating_in_mix_date(count):
    mix_count = int(count)
    all_mix = read_csv('mixdata.csv')

    all_mix[mix_count][len(all_mix[mix_count]) - 1] = int(all_mix[mix_count][len(all_mix[mix_count]) - 1]) + 1

    save_list_to_csv('mixdata.csv', all_mix)


def find_mix_by_count(count: int) -> list:
    all_mix = read_csv('mixdata.csv')

    min_count = int(all_mix[0][0])
    max_count = int(all_mix[len(all_mix) - 1][0])

    if min_count <= count <= max_count:
        return all_mix[count]
    else:
        return []


def find_match():
    """Функция поиска совпадающих строк в списке миксов"""
    buff_mix = []
    all_mix = read_csv('mixdata.csv')

    for row in range(0, len(all_mix)):
        get_mix = []
        for flavor in range(0, len(all_mix[row])):
            get_mix.append(all_mix[row][flavor])
        for j in range(row + 1, len(all_mix)):

            match = 0
            for flavor in get_mix:
                if flavor in all_mix[j]:
                    match += 1

            if match == len(get_mix) and len(get_mix) == len(all_mix[j]):
                buff_mix.append(all_mix[row])
                buff_mix.append(row+1)
                buff_mix.append(j+1)

    print(buff_mix)


def flavors_stats():
    all_flavors = read_csv('flavors.csv')
    all_mix = read_csv('mixdata.csv')

    for count in range(0, len(all_flavors)):
        for mix in all_mix:
            if all_flavors[count][0].lower() in mix:
                all_flavors[count][2] = int(all_flavors[count][2]) + 1

    save_list_to_csv('flavors.csv', all_flavors)


def main():
    find_match()
    # print(find_mix_by_count(110))
    # flavors_stats()
    # change_rating_in_mix_date('1')


if __name__ == "__main__":
    main()

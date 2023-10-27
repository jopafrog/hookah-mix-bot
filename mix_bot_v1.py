import telebot
from datetime import datetime
import excelsave
from random import randint
from dotenv import load_dotenv
from os import getenv
import statistics


load_dotenv()
DIRECTORY = getenv("DIRECTORY")


def filter_flavor(flavor_input: str) -> list:
    flavor_list = []
    symbols_to_remove = ",!?+()-"

    for symbol in symbols_to_remove:
        flavor_input = flavor_input.replace(symbol, " ")

        flavor_list = flavor_input.split()

    """Стандартизируем написание элементы для поиска"""
    num = 0
    while num < len(flavor_list):
        if len(flavor_list[num]) < 3:
            flavor_list.remove(flavor_list[num])

        elif "кола" in flavor_list[num].lower() and flavor_list[num].lower() != "шоколад":
            flavor_list[num] = "cola"
            num += 1

        elif "холодок" in flavor_list[num].lower() or "лед" in flavor_list[num].lower():
            flavor_list[num] = "холод"
            num += 1

        elif "мёд" in flavor_list[num].lower():
            flavor_list[num] = "мед"
            num += 1

        elif "черная" in flavor_list[num].lower():
            flavor_list.remove(flavor_list[num])

        elif flavor_list[num].lower() == "двойное" and flavor_list[num+1].lower() == "яблоко":
            flavor_list[num] = "двойное яблоко"
            flavor_list.remove(flavor_list[num+1])
            num += 1

        elif flavor_list[num].lower() == "зеленый" and flavor_list[num+1].lower() == "чай":
            flavor_list[num] = "зеленый чай"
            flavor_list.remove(flavor_list[num + 1])
            num += 1

        else:
            num += 1

    return flavor_list


bot = telebot.TeleBot(getenv("TOKEN"))


@bot.message_handler(commands=['start'])
def start(message):
    print(datetime.now(), "Новый пользователь бота", message.chat.id)
    bot.send_message(message.chat.id, "Привет! Я знаю 200+ миксов для кальяна")
    bot.send_message(message.chat.id, "Просто напиши несколько вкусов которые хочется, а я их с чем-нибудь смешаю")


@bot.message_handler(commands=['abc'])
def handbook(message):
    print(datetime.now(), "Вход в алфавитный указатель, чат", message.chat.id)
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=6)
    buttons = []
    for letter in "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ":
        button = telebot.types.InlineKeyboardButton(letter, callback_data=letter)
        buttons.append(button)

    for button_num in range(0, 29, 6):
        if button_num != 24:
            keyboard.add(buttons[button_num], buttons[button_num+1], buttons[button_num+2],
                         buttons[button_num+3], buttons[button_num+4], buttons[button_num+5])
        else:
            keyboard.add(buttons[button_num], buttons[button_num + 1],
                         buttons[button_num + 2], buttons[button_num + 3])

    bot.send_message(message.chat.id, "Алфавитный указатель по вкусам табака", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ":
        print(datetime.now(), "Запрос списка вкусов, чат", call.message.chat.id, "Буква", call.data)

        flavor_list = excelsave.find_first_letter(call.data)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)

        for flavor in flavor_list:
            button = telebot.types.InlineKeyboardButton(flavor, callback_data=flavor)
            keyboard.add(button)

        bot.send_message(call.message.chat.id, "Вот какие вкусы есть", reply_markup=keyboard)

    elif "mix" in call.data:
        print(datetime.now(), "Запрос вкусов микса -", call.data, "чат", call.message.chat.id, )
        text = call.data.split(' ')

        '''Забираем из списка миксов нужный нам, и отбрасываем элементы, кроме вкусов'''
        flavor_list = statistics.find_mix_by_count(int(text[1]))
        flavor_list.remove(flavor_list[0])
        flavor_list.pop()

        statistics.change_rating_in_mix_date(int(text[1]))  # обновляем спрос на микс

        for item in range(0, len(flavor_list)):
            top_list = excelsave.read_file(flavor_list[item])

            bot.send_message(call.message.chat.id, f"--- Табаки вкуса {flavor_list[item]} ---")
            statistics.change_rating_in_flavors_list(flavor_list[item])

            if len(top_list) >= 4:
                max_range = 4
            else:
                max_range = len(top_list)

            for num in range(1, max_range):
                bot.send_message(call.message.chat.id, top_list[num])

    else:
        print(datetime.now(), "Запрос топа по вкусу -", call.data, "чат", call.message.chat.id, )
        statistics.change_rating_in_flavors_list(call.data)  # Обновляем спрос на вкус

        top_list = excelsave.read_file(str(call.data))

        bot.send_message(call.message.chat.id, f"--- Вот лучшие табаки со вкусом {call.data} ---")
        for num in range(0, len(top_list)):
            if num >= 10:
                break
            else:
                bot.send_message(call.message.chat.id, top_list[num])


@bot.message_handler(commands=['add'])
def add(message):
    flavor_input = message.text
    flavors_get = filter_flavor(flavor_input)
    flavors_get.remove(flavors_get[0])  # удаляем первый элемент списка вкусов так как это "/add

    new_mix = False
    all_mix = statistics.read_csv('mixdata.csv')

    for mix in all_mix:
        mix.remove(mix[0])
        mix.pop()

        match = 0
        for flavor in flavors_get:
            if flavor in mix:
                match += 1

        if match >= len(mix):
            bot.send_message(message.chat.id, "Микс уже есть в списке")
            new_mix = False
            break

        else:
            new_mix = True

    if new_mix:
        print(datetime.now(), "(!) Запрос на добавление микса, чат", message.chat.id)

        with open(DIRECTORY + "addmixlist.txt", "a", encoding='utf-8') as file:
            text = message.text[4:len(message.text):1]
            file.write(text + '\n')

        bot.send_message(message.chat.id, "Ух ты, новый микс, спасибо!")
        bot.send_message(message.chat.id, "Через какое-то время он появится в базе")


@bot.message_handler(commands=['top'])
def top100(message):
    print(datetime.now(), "Запрос на Топ100, чат", message.chat.id)

    bot.send_message(message.chat.id, 'Вот ТОП10 лучших табаков:')
    tobacco_list = statistics.read_csv('top100.csv', True)
    for item in range(0, 10):
        row = f'{item+1}. {tobacco_list[item][0]} / {tobacco_list[item][1]} ({float(tobacco_list[item][3]):.3f})'
        bot.send_message(message.chat.id, row)


@bot.message_handler(commands=['topbrand'])
def top_brands(message):
    print(datetime.now(), "Запрос на Топ Брендов, чат", message.chat.id)

    bot.send_message(message.chat.id, 'Вот ТОП10 лучших брендов табака:')
    brands_list = statistics.read_csv('topBrands.csv', True)
    for item in range(0, 10):
        row = f'{item+1}. {brands_list[item][0]} ({float(brands_list[item][2]):.3f})'
        bot.send_message(message.chat.id, row)


@bot.message_handler(content_types=['text'])
def search(message):
    buff_mix = []

    flavors_get = filter_flavor(message.text)

    if len(flavors_get) == 1:
        print("Ввод вкуса:", message.text)
        top_list = excelsave.read_file(str(flavors_get[0]).lower())

        if len(top_list) > 0:
            bot.send_message(message.chat.id, f"- Лучшие табаки со вкусом {message.text} -")
            statistics.change_rating_in_flavors_list(str(flavors_get[0]).lower())  # Обновляем спрос на вкус

            for num in range(0, len(top_list)):
                if num < 10:
                    bot.send_message(message.chat.id, top_list[num])

        else:
            bot.send_message(message.chat.id, "Я не знаю такой вкус")
            bot.send_message(message.chat.id, "Попробуй поискать его в Алфавите вкусов (/abc)")

    elif len(flavors_get) > 1:
        print(datetime.now(), "Запрос микс", message.text, "чат", message.chat.id, )
        all_mix = statistics.read_csv('mixdata.csv')

        for mix in all_mix:
            match = 0
            for flavor in flavors_get:
                if flavor.lower() in mix:
                    match += 1

            if match >= 2:
                buff_mix.append(mix)

        if len(buff_mix) == 0:
            bot.send_message(message.chat.id, "Такое вам не смешать")
            instruction_text = "Если хочешь добавить свой микс в базу, напишите /add {вкусы своего микса}"
            bot.send_message(message.chat.id, instruction_text)
            print("(!)", datetime.now(), "Запрос микса - неудача, чат", message.chat.id)
            print("Присланное сообщение:", message.text)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)

            print(buff_mix)

            if len(buff_mix) > 5:
                buff_rand_mix = []
                while len(buff_rand_mix) < 5:
                    rand = randint(0, len(buff_mix)-1)
                    if rand not in buff_rand_mix:
                        buff_rand_mix.append(rand)

                for num in buff_rand_mix:
                    mix = buff_mix[num]
                    mix_count = mix[0]
                    mix.pop()
                    mix.remove(mix[0])
                    row_mix = ' + '.join(mix)
                    button = telebot.types.InlineKeyboardButton(row_mix, callback_data=f"mix {mix_count}")
                    keyboard.add(button)

            else:
                for mix in buff_mix:
                    mix_count = mix[0]
                    mix.pop()
                    mix.remove(mix[0])
                    row_mix = ' + '.join(mix)

                    button = telebot.types.InlineKeyboardButton(row_mix, callback_data=f"mix {mix_count}")
                    keyboard.add(button)

            bot.send_message(message.chat.id, "--- Вот несколько вариантов миксов ---", reply_markup=keyboard)


bot.polling(none_stop=True)

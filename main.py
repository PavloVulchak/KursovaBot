# Підключення бібліотек
import get_ISS_flyover_information as ISSflyover
import get_location_from_name as ParseLocation
import get_post_webex_api as WebexAPI
import get_Weather as Weather
import requests
import datetime

# змінна в якій буде зберігатися Id вибраної кімнати
roomIdToGetMessages = None

# функція для отримання списку кімант і вибір кімнати через пошук за назвою і збереження Id цієї кімнати
def initialisation():
    global roomIdToGetMessages
    # отримання списку кімнат в Webex
    rooms = WebexAPI.get_list_rooms_webex()
    print("Список кімнат:")
    # виводжу список кімнат в термінал
    for room in rooms:
        print (room["title"])

    # Шукаємо назву кімнати та записуємо її назву в терміналі
    while True:
        # Введення назву кімнати, яку потрібно шукати
        roomNameToSearch = input("Which room should be monitored for send messages with webex bot? ")

        # призначаю змінну, яка буде містити Id вибраної кімнати
        roomIdToGetMessages = None
        for room in rooms:
            # Пошук назви кімнати за допомогою змінної roomNameToSearch
            if (room["title"] == roomNameToSearch):
                # Відображення кімнати, знайденої за допомогою змінної roomNameToSearch з додатковими параметри
                print("Found rooms with the word " + roomNameToSearch)

                # Збереження ідентифікатора кімнати та назву кімнати у змінні
                roomIdToGetMessages = room["id"]
                roomTitleToGetMessages = room["title"]
                print("Found room : " + roomTitleToGetMessages)
                break
        # перевірка чи в змінні roomIdToGetMessages є записано id знайденої кімнати
        if (roomIdToGetMessages == None):
            print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
            print("Please try again...")
        else:
            break
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з часом початку перельоту і його тривалістю
# відносно отриманого повідомлення з назвою місця розташування і Id кімнати в яку буде надсилатися повідомлення
def cmd_ISS_Location(messages, msg_id):
    # збереження тексту першого повідомлення в масиві
    message = messages[0]["text"]
    try:
        # отриманна назви місця розташування з вхідного повідомлення
        location = message[13:]
        # отримання координат місця розташування відносно введеної назви місця розташування
        json_data_location = ParseLocation.get_Location(location)
        # збереження місцезнаходження, отримане від MapQuest API, у змінній
        locationResults = json_data_location["results"][0]["providedLocation"]["location"]
        print("Розташування: " + locationResults)
        # збереження в змінних широту та довготу GPS, отримані від API MapQuest
        locationLat_Lng = json_data_location["results"][0]["locations"][0]["latLng"]
        locationLat = locationLat_Lng["lat"]
        locationLng = locationLat_Lng["lng"]
        # виведення в терміналі адресу розташування
        print("Розташування в GPS координатах: " + str(locationLat) + ", " + str(locationLng))

        # отримання час підйому та тривалість першого перельоту відносно ортиманих координат місця розташування
        risetime_durationInEpochSeconds = ISSflyover.get_ISS_flyover(locationLat_Lng)
        # збереження час підйому та тривалість першого перельоту у змінну
        risetimeInEpochSeconds = risetime_durationInEpochSeconds["risetime"]
        durationInSeconds = risetime_durationInEpochSeconds["duration"]
        # перетворити час підйому, який повертає служба API, у час Unix Epoch
        risetimeInFormattedString = str(datetime.datetime.fromtimestamp(risetimeInEpochSeconds))

        # зібірка повідомлення-відповіді
        responseMessage = f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n" \
                          f"Для місця розташування '{locationResults}' з координатами широти: {locationLat} і довготи {locationLng}\n" \
                          f"Початок першого перельоту МКС над заданими місцем буде: {risetimeInFormattedString}\n" \
                          f"Тривалість перельоту становить: {durationInSeconds} секунд.\n" \
                          f"Гарного дня!"
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до webex API
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages=msg_id)

    except:
        # зібірка повідомлення-відповіді про помилку
        responseMessage = "Ви ввели неправильні дані."
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до webex API
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages=msg_id)
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з даними про погоду в даний момент
# відносно отриманого повідомлення з назвою місця розташування і Id кімнати в яку буде надсилатися повідомлення
def cmd_weather(messages, msg_id):
    # збереження тексту першого повідомлення в масиві
    message = messages[0]["text"]
    try:
        # отриманна назви місця розташування з вхідного повідомлення
        name_location = message[9:]
        # отримання даних про погоду відносно отриманої назви місця розташування
        weather_data = Weather.get_Weather_API(name_location)
        # збереження в змінну назву місця для якого виконувався запит на погоду, отриманого від API OneWeatherMap
        city = weather_data["name"]
        # збереження в змінну назву погодного явища і відповідно до нього емозді
        weather_description = weather_data["weather"][0]["main"]
        if weather_description in Weather.code_to_smile:
            weather_smile = Weather.code_to_smile[weather_description]
        else:
            weather_smile = "Немає даних про погоду."

        # збереження в змінну значення температури повітря
        current_weather = weather_data["main"]["temp"]
        # збереження в змінну значення воллогості повітря
        humidity = weather_data["main"]["humidity"]
        # збереження в змінну значення атмосферного тиску
        pressure = weather_data["main"]["pressure"]
        # збереження в змінну значення швидкості вітру
        wind = weather_data["wind"]["speed"]
        # збереження в змінні значення часу сходу і заходу сонця
        sunrise_timestamp = datetime.datetime.fromtimestamp(weather_data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(weather_data["sys"]["sunset"])
        # збереження в змінну значення часу тривалості дня
        lengh_of_the_day = sunset_timestamp - sunrise_timestamp
        # збереження в змінну значення реального часу і дати
        current_time = datetime.datetime.fromtimestamp(weather_data["dt"])

        # Відправлення повідомлення-відповіді до webex API
        responseMessage = f"***{current_time}***\n" \
                          f"Погода в місті: {city}\n{weather_smile}\nТемпература: {current_weather} C°\n" \
                          f"Вологість: {humidity}%\nТиск: {pressure} мм.рт.ст\nВітер: {wind} м/с\n" \
                          f"Схід сонця: {sunrise_timestamp}\nЗахід сонця: {sunset_timestamp}\nТривалість дня: {lengh_of_the_day}\n" \
                          f"Гарного дня!"

        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до API webex
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)

    except:
        # Відправлення повідомлення-відповіді про помилку
        responseMessage = "Ви ввели неправильні дані."
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до API webex
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)
    return 0

# Функція яка порертає рядок з тою кількість пробілів яку задає користувач
def space(n):
    str_space=""
    for i in range(n):
        str_space += " "
    return str_space

# відправлення повідомлення-відповіді в Webex кімнату з даними про курс валют
# відносно отриманого повідомлення з Id кімнати в яку буде надсилатися повідомлення
def cmd_kursvalut(messages, msg_id):
    # отримання мінімального списку для курса валют
    response = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=11").json()
    # отримання доповняльного списку для курса валют
    response = response + requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=12").json()
    try:
        # збереження тексту першого повідомлення в масиві
        message = messages[0]["text"]
        # змінна яка містить назву курса валют
        name_kursvalut = ""
        # Перевірка чи користував ввів команду і параметр до неї у вигляді назви курсу
        if (len(message) > 11):
            # записуємо в змінну назву для пошуку вибраного курса валют
            name_kursvalut = message[11:]

        # зібірка заголовку в таблиці для повідомлення-відповіді
        responseMessage = f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n" \
                          f"| Купівля{space(12 - 7)}| Курс{space(10 - 5)}| Продаж{space(12 - 7)}| Відносно курсу |\n" \
                          f"| -------{space(12 - 7)}| ----{space(10 - 5)}| ------{space(12 - 7)}| -------------- |\n"
        # перебір кожного окремого курсу в отриманих даних курсу валют
        for coin in response:
            # вибираємо курс валют який ми вводили для пошуку сиред інших курсів валют або
            # вибирається будь-який курс коли користувач не ввів назву для пошуку
            if (not coin['ccy'] == "BTC") & ((name_kursvalut == coin['ccy']) | (name_kursvalut == "")):
                # додавання даних в таблицю для повідомлення-відповіді
                responseMessage = responseMessage + f"| {coin['buy']}{space(12 - len(coin['buy']))}|" \
                                                    f" {coin['ccy']}{space(9 - len(coin['ccy']))}|" \
                                                    f" {coin['sale']}{space(11 - len(coin['sale']))}|" \
                                                    f" {coin['base_ccy']}{space(14 - len(coin['base_ccy']))} |\n"
        # додавання тексту до повідомлення-відповіді
        responseMessage = responseMessage + "Гарного дня!"
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)
        responseMessage = "<pre>" + responseMessage + "</pre>"
        # Відправлення повідомлення-відповіді до API webex
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages=msg_id, mode="html")
    except:
        # Відправлення повідомлення-відповіді про помилку
        responseMessage = "Сталася неочікувана помилка."
        # виведення повідомлення-відповідь в терміналі
        print("Відправлення до Webex Teams: " + responseMessage)

        # Відправлення повідомлення-відповіді до API webex
        WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages=msg_id)
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з інформацією про вміння цього бота
# відносно отриманої Id кімнати в яку буде надсилатися повідомлення
def cmd_start(msg_id):
    # зібірка повідомлення-відповіді
    responseMessage = "Ви запустили бота. \nЦей бот має такі можливості: \n" \
                      "\t- Виводить дату і час першого імовірного перельоту МКС над координатами місця яке було введено.\n" \
                      "\t- Виводить дані про погоду на сьогодні для місця яке було введено\n" \
                      "\t- Виводить дані про курс валют на даний момент і виводить у формі таблиці\n" \
                      "\t- За допомогою команд '/help' і '/start' можна отримати інформацію про опис команд, " \
                      "які може виконувати бот і загальну інформацію про нього відповідно. "

    # виведення повідомлення-відповідь в терміналі
    print("Відправлення до Webex Teams: " + responseMessage)

    # Відправлення повідомлення-відповіді до API webex
    WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)
    return 0

# відправлення повідомлення-відповіді в Webex кімнату з інформацією про команди яакі бот може виконувати
# відносно отриманої Id кімнати в яку буде надсилатися повідомлення
def cmd_help(msg_id):
    # зібірка повідомлення-відповіді
    responseMessage = "Цей бот може виконувати такі команди: \n" \
                      "-\t'/help' - ця команда повернтає список достурпних команд і інформацію про них\n" \
                      "-\t'/start' - ця команда запускається в основному напочатку, а як результат вона надсилає інформацію про можливості бота\n" \
                      "-\t'/isslocation {location}' - ця команда виводить дату і час першого імовірного перельоту МКС над координатами місця яке було введено.\n" \
                      "Приклад запуску: '/isslocation Rivne'\n" \
                      "Примітка: місце розташування вводити на англійські мові, " \
                      "якщо ж будете використовуватии іншу мову то можуть виникнути неочікувані результати\n" \
                      "-\t'/weather {location}' - ця команда виводить дані про погоду на сьогодні для місця яке було введено.\n" \
                      "Приклад запуску: '/weather Lviv'\n" \
                      "-\t'/kursvalut' - ця команда виводить повну таблицю з курсом валют\n" \
                      "-\t'/kursvalut {name}' - ця команда виводить таблицю з курсомдля введеної валюти, де {name} - назва валюти в форматі\n" \
                      "Приклад запуску: '/kursvalut USD'\n"
    # виведення повідомлення-відповідь в терміналі
    print("Відправлення до Webex Teams: " + responseMessage)

    # Відправлення повідомлення-відповіді до API webex
    WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)
    return 0

# основна програма бота
if __name__ == '__main__':
    # отримуємо список кімант і вибираємо кімнату через пошук за назвою і зберігаємо Id цієї кімнати
    initialisation()
    # змінна в якій буде міститися ID останнього повідомлення
    msg_id = "0"
    # запускайте цикл "bot" він буде виконуватися доки не буде зупинено вручну або не станеться виняток
    while True:
        # отримання останнього повідомлення з вибраної кімнати в Webex
        messages = WebexAPI.get_last_massages_webex(roomIdToGetMessages, 1)
        # збереження тексту першого повідомлення в масиві
        message = messages[0]["text"]

        # перевірка чи Id отриманого повідомлення було збережено тобто чи дане повідомлення переглядалося раніше
        if msg_id != messages[0]["id"]:
            # якщо повідомлення нове то виводимо його в термінал
            print("Отримане повідомлення: " + message)
            # зберігаємо Id нового повідомлення в змінну
            msg_id = messages[0]["id"]
            # перевірка, чи починається текст повідомлення з ключового символу "/".
            if message.find("/") == 0:
                # перевірка на те яка команда була надіслана через повідомлення і запускає відповідну функцію
                # якщо команда не коректна то бот відправляє відповідне повідомлення
                if message == "/start":
                    cmd_start(msg_id)
                elif message.find("/isslocation") == 0:
                    cmd_ISS_Location(messages, msg_id)
                elif message.find("/weather") == 0:
                    cmd_weather(messages, msg_id)
                elif message.find("/kursvalut") == 0:
                    cmd_kursvalut(messages, msg_id)
                elif message == "/help":
                    cmd_help(msg_id)
                else:
                    # зібірка повідомлення-відповіді про помилку
                    responseMessage = "Ви ввели некоректну команду."
                    # виведення повідомлення-відповідь в терміналі
                    print("Відправлення до Webex Teams: " + responseMessage)

                    # Відправлення повідомлення-відповіді до webex API
                    WebexAPI.post_send_massage_webex(roomIdToGetMessages, responseMessage,parentId_To_Get_Messages=msg_id)


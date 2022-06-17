import requests
import json
import config
# функція для надсилання Get запиту для отримання списку кімнат в Webex
def get_list_rooms_webex():
    # записуємо в змінну токен для Webex
    accessToken = "Bearer " + config.hard_Token_webex
    # Отримання інформацію про список кімнат в Webex за допомогою методу HTTP GET
    r = requests.get("https://api.ciscospark.com/v1/rooms",
                     headers={"Authorization": accessToken}
                     )
    # Перевірка, чи відповідь від виклику API була в порядку (р. код 200)
    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    # отримання повернутих даних у форматі json
    rooms = r.json()["items"]
    return rooms

# функція для надсилання Get запиту для отримання списку остатних повідомлень
# в Webex при введених параметрах: Id кімнати і максимальну кількість повідомлень
def get_last_massages_webex(roomId_To_Get_Messages, count_last_massage):
    # параметри GET Webex Teams
    # "roomId" - це ідентифікатор вибраної кімнати
    # "max": 1 обмеження, щоб отримати лише останнє повідомлення в кімнаті
    GetParameters = {
        "roomId": roomId_To_Get_Messages,
        "max": count_last_massage
    }
    # записуємо в змінну токен для Webex
    accessToken = "Bearer " + config.hard_Token_webex
    # Отримання інформацію про список останніх повідомлень в Webex за допомогою методу HTTP GET
    r = requests.get("https://api.ciscospark.com/v1/messages",
                     params=GetParameters,
                     headers={"Authorization": accessToken}
                     )
    # перевірка, чи повернутий код статусу HTTP 200/OK
    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

    # отримати дані у форматі JSON
    json_data = r.json()
    # перевірка, чи є повідомлення в масиві "items".
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # збереження масиву повідомлень
    massages = json_data["items"]
    return massages

# функція для надсилання Post запиту створення і відправлення повідомлень з можливістю відповідати на повідомлення з командою
# в Webex при введених параметрах: Id кімнати, текст повідомлення, Id батківського повідомлення і формату повідомлення (text, markdown, html)
def post_send_massage_webex(roomIdToGetMessages, responseMessage, parentId_To_Get_Messages, mode="text"):
    # записуємо в змінну токен для Webex
    accessToken = "Bearer " + config.hard_Token_webex
    # заголовок HTTP Webex Teams, включають заголовок Content-Type для даних POST JSON
    HTTPHeaders = {
        "Authorization": accessToken,
        "Content-Type": "application/json"
    }
    # дані Webex Teams POST JSON
    # "roomId" - це ідентифікатор вибраної кімнати
    # mode - це тип повідомлення-відповідь, зібране вище
    # "parentId" - це ідентифікатор батківського повідомлення тотбо до якого ми будем прикріплювати відповідь
    PostData = {
        "roomId": roomIdToGetMessages,
        "parentId": parentId_To_Get_Messages,
        mode: responseMessage
    }
    # Надселання повідомлення в Webex за допомогою методу HTTP POST
    r = requests.post("https://api.ciscospark.com/v1/messages",
                      data=json.dumps(PostData),
                      headers=HTTPHeaders
                      )
    # Перевірка, чи повідомлення було надіслано успішно і повернуті дані JSON із служби API містять код статусу який дорівнює 200
    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

    return r
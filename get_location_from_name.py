import config
import requests
# функція для надселання Get запиту яка повертає координати розташування за заданою назвою місця розташування
def get_Location(name_loction):
    # GET параметри для API MapQuest
    # "location" - це місце пошуку
    # "key" - це секретний ключ API, який я створив на https://developer.mapquest.com/user/me/apps
    mapsAPIGetParameters = {
        "location": name_loction,
        "key": config.mapquest_API_Key
    }
    # Отримання інформацію про місцезнаходження за допомогою служби геокодування MapQuest API за допомогою методу HTTP GET
    r = requests.get("https://www.mapquestapi.com/geocoding/v1/address",
                     params=mapsAPIGetParameters
                     )
    # отримані дані у форматі json
    json_data = r.json()
    # перевіряє, чи є ключ статусу у повернених даних JSON "OK"
    if not json_data["info"]["statuscode"] == 0:
        raise Exception("Incorrect reply from MapQuest API. Status code: {}".format(r.statuscode))

    return json_data
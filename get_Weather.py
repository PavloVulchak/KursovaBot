import config
import requests

# масив даних з назвою погодного явища і відповідного до нього смайлика або картинки
code_to_smile = {
    "Clear": "Сонячно \U00002600",
    "Clouds": "Хмарно \U00002601",
    "Rain": "Дощ \U00002614",
    "Drizzle": "Дощ \U00002614",
    "Thunderstorm": "Гроза \U000026A1",
    "Snow": "Сніг \U0001F328",
    "Mist": "Туман \U0001F32B",
}

# функція для надселання Get запиту для отримання даних про погоду за заданою назвою місця розташування
def get_Weather_API(name_location):
    # GET параметри для API запитів про погоду
    # "q" - це назва місця розташування
    # "units" - це вибір одиниці виміру
    # "appid" - це секретний ключ API, який я створив на https://home.openweathermap.org/api_keys
    weatherAPIGetParameters = {
        "q": name_location,
        "units": "metric",
        "appid": config.open_weather_key
    }
    # Отримання інформацію про місцезнаходження за допомогою служби геокодування Weather API за допомогою методу HTTP GET
    r = requests.get("https://api.openweathermap.org/data/2.5/weather",
                     params=weatherAPIGetParameters
                     )
    # отримані дані у форматі json
    json_data = r.json()
    # Перевірка чи запит виконався успішно і чи status дорівнює 200
    if not json_data["cod"] == 200:
        raise Exception("Incorrect reply from MapQuest API. Status code: {}".format(r.statuscode))

    return json_data
import requests
# функція для надсилання Get запиту про перший переліт МКС над заданими координатами
def get_ISS_flyover(location):
    # GET API параметри перельоту МКС
    # "lat" - це широта розташування
    # "lon" - це довгота розташування
    issAPIGetParameters = {
        "lat": location["lat"],
        "lon": location["lng"]
    }
    # Отримання інформацію про проліт МКС за вказаними координатами GPS за допомогою методу HTTP GET
    r = requests.get("http://api.open-notify.org/iss-pass.json",
                     params=issAPIGetParameters
                     )
    # отримання повернутих даних у форматі json
    json_data = r.json()
    # Перевірка, чи повернуті дані JSON із служби API в порядку та містять ключ "response".
    if not "response" in json_data:
        raise Exception(
            "Incorrect reply from open-notify.org API. Status code: {}. Text: {}".format(r.status_code, r.text))

    # збереження часу підйому та тривалість першого перельоту у змінну
    risetime_durationInEpochSeconds = json_data["response"][0]
    return risetime_durationInEpochSeconds
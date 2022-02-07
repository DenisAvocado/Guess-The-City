import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
import random

CITIES = ['Лондон', 'Нью-Йорк', 'Москва', 'Париж',
          'Минск', 'Киев', 'Пекин', 'Вашингтон', 'Санкт-Петербург',
          'Омск', 'Оттава', 'Сеул', 'Токио', 'Стамбул', 'Берлин',
          'Варшава', 'Мадрид', 'Амстердам', 'Осло', 'Стокгольм']


def get_ll(address):
    toponym_to_find = address

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        return False

    json_response = response.json()
    try:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coordinates = [float(x) for x in toponym["Point"]["pos"].split()]

        spn = str(random.uniform(0.002, 0.02))
        la, lo = toponym_coordinates[0] + random.uniform(0.001, 0.1),\
                    toponym_coordinates[1] + random.uniform(0.001, 0.05)
        ll = ' '.join([str(la), str(lo)])
    except Exception:
        return False

    return ll, spn


def get_image(ll, spn):
    request = f'https://static-maps.yandex.ru/1.x/?ll={",".join(ll.split())}' \
              f'&l={random.choice(["map", "sat"])}&spn={",".join([spn, spn])}'
    response = requests.get(request)
    if not response:
        return False

    image = Image.open(BytesIO(response.content))
    image.save('random_city.png')
    return image


used = []


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('guess_city.ui', self)
        self.button.clicked.connect(self.game)
        self.city_line.hide()
        self.label.hide()
        self.cur_city = ''
        self.wins = 0
        self.do = True

    def game(self):
        if self.do:
            if self.button.text() == 'Начать':
                self.city_line.show()
                self.label.show()
                self.cur_city = random.choice(CITIES)
                while self.cur_city in used:
                    self.cur_city = random.choice(CITIES)
                get_image(*get_ll(self.cur_city))
                pixmap = QPixmap('random_city.png')
                self.img_city.setPixmap(pixmap)
                self.button.setText('ОК')
            elif self.button.text() == 'ОК':
                used.append(self.cur_city)
                if self.cur_city.lower() == self.city_line.text().lower():
                    self.total_lab.setText('Правильный ответ!')
                    self.button.setText('Далее')
                    self.wins += 1
                else:
                    self.total_lab.setText(f'Неудача! Это {self.cur_city}')
                    self.button.setText('Далее')
                if len(used) == len(CITIES):
                    self.total_lab.setText(f'Игра окончена! Правильных ответов: {self.wins}')
                    self.button.setText('Молодец!')
                    self.do = False
            elif self.button.text() == 'Далее':
                self.city_line.setText('')
                self.cur_city = random.choice(CITIES)
                while self.cur_city in used:
                    self.cur_city = random.choice(CITIES)
                get_image(*get_ll(self.cur_city))
                pixmap = QPixmap('random_city.png')
                self.img_city.setPixmap(pixmap)
                self.button.setText('ОК')
                self.total_lab.setText('')
            else:
                self.statusBar().showMessage('Что-то пошло не так')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


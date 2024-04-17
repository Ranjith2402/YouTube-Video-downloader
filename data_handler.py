import json

# "https://www.youtube.com/embed/nkNC6gyogNc
# "https://youtu.be/s8C4-kYJjOw"


class DataLoader:
    data = {}
    cwd = '.'
    __DATA = {'isVerified': True,
              'downloaded': [],
              'previous_quality': '360p',
              'color_pallet': 'Blue',
              'theme': 'Light',
              'is_banned': True,
              'age restrict': True,
              'result limit': 5,
              'auto download': False,
              'follow system theme': False,
              'ui_mode': 1,
              'last link': '',
              'isAgree to T&C': False,
              'last error file': ''}

    def create(self):
        with open('data.json', 'w+'):
            pass
        self.data = {}
        for item, value in self.__DATA.items():
            self.data[item] = value
        self.save()
        self.load()
        return self

    def load(self):
        try:
            with open('data.json', 'r') as file:
                self.data = json.load(file)
        except json.decoder.JSONDecodeError:
            self.create()

    def save(self, data=None):
        if data is not None:
            self.data = data
        with open(self.cwd + '/' + 'data.json', 'w+') as file:
            json.dump(self.data, file)


if __name__ == '__main__':
    _engine = DataLoader()
    _engine.load()
    print(_engine.data)
    _engine.create()
    print(_engine.data)

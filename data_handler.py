import json


def create():
    with open('data.json', 'w+'):
        pass
    engine = DataLoader()
    engine.data['isVerified'] = True
    engine.data['downloaded'] = []
    engine.data['previous_quality'] = '360p'
    engine.data['color_pallet'] = 'Blue'
    engine.data['theme'] = 'Light'
    engine.data['is_banned'] = True
    engine.data['age restrict'] = True
    engine.data['result limit'] = 5
    engine.data['auto download'] = False
    engine.data['follow system theme'] = False
    engine.data['ui_mode'] = 1
    engine.data['last link'] = ''
    engine.data['isAgree to T&C'] = False
    engine.save()
    engine.load()
    return engine


class DataLoader:
    data = {}
    cwd = '.'

    def load(self):
        try:
            with open('data.json', 'r') as file:
                self.data = json.load(file)
        except json.decoder.JSONDecodeError:
            create()

    def save(self, data=None):
        if data is not None:
            self.data = data
        with open(self.cwd + '/' + 'data.json', 'w+') as file:
            json.dump(self.data, file)


if __name__ == '__main__':
    _engine = DataLoader()
    _engine.load()
    print(_engine.data)
    a = create()
    print(a.data)

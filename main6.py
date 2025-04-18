# country = {(5, 6): 3}
# print(country[(5, 6)])

# country = {'code': 'RU', 'name': 'Russian', 'population': 144}
# country = dict(code='RU', name='Russian')
# print(country['name'])

# print(country.items())

# country = {'code': 'RU', 'name': 'Russian', 'population': 144}
# for key, value in country.items():
#     print(key, ' - ', value)
#
# code - RU
# name - Russian
# population - 144

# country = {'code': 'RU', 'name': 'Russian', 'population': 144}

# print.clear() полностью очищает словарь
# print.pop('name') удаляет выбранный элемент и что входило в него
#country.popitem() удаляет последний элемент в словаре и его число
# country['code'] = 'None' меняет элемент словаря на написанный

person = {
    'user_1': {
        'first name': 'John',
        'last name': 'Marley',
        'age': 45,
        'address': ['г. Москва', 'ул. лаптиева', '45'],
        'grades': {'math': 5, 'physics': 3}
    },
    'user_2': {

    }
}

print(person['user_1']['address'][1]) 
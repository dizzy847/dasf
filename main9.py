# try:
#     x = int(input('Введите число: '))
#     x += 5
#     print(x)
# except ValueError:
#     print('Введите число, а не слово!!!')
#
# x = 0
# while x == 0:
#     try:
#         x = int(input('Введите число: '))
#         x += 5
#         print(x)
#     except ValueError:
#         print('Введите число, а не слово!!!')

try:
    x = 5 / 1
    x = int(input())
except ZeroDivisionError:
    print('Деление на ноль нельзя')
except ValueError:
    print('Вы ввели что-то не так')
else:
    print('else') # else выполняется тогда когда не выполняются except, то есть нет ошибок
finally:
    print('Finally') # finally выполняется всегда вне зависимости от except

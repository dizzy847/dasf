# num1 = int(input('Введите первое число: '))

# num2 = int(input('Введите второе число: '))

# num1 +=5 # добавление к

# print('Result:', num1 + num2)
# print('Result:', num1 - num2)
# print('Result:', num1 / num2)
# print('Result:', num1 * num2)
# print('Result:', num1 ** num2)
# print('Result:', num1 // num2)
# print('Result:', num1 // num2)
# print('Result:', num1 // num2)
# print('Result:', num1 // num2)

# data = input('Введите слово:')
# number = 5 if data == 'Five' else 0
# print(number)

n = int(input('Enter lenght: '))

user_list = []

i = 0
while i < n:
    string = 'Enter element #' + str(i + 1) + ': '
    user_list.append(input(string))
    i += 1

print(user_list)
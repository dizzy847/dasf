# data = input("Введите текст: ")
#
# file = open('data/text.txt', 'w') # w стирает все данные с файла, a как append добавляет не удаляя данные
#
# file.write('Hello\n')
# file.write(data + "\n")
#
# file.close()

file = open('data/text.txt', 'r') # r чтение файла

# print(file.read())
for line in file:
    print(line, end="")

file.close()
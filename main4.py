# for i in range(1, 6, 2):
#     print(i)

# Вывод 1 3 5s

# Вывод 1 3 5



# count = 0
# word = 'Hello world!'
# for i in word:
#     if i == 'l':
#         count += 1
#
# print('Count:', count)


# isHasCar = True
#
# while isHasCar:
#     if input('Enter data:') == 'Stop':
#         isHasCar = False


# found = None
# for i in 'Hello':
#     if i == 'r':
#         found = True
#         break
# else:
#     found = False
#
# print(found)


# nums = [3434, 34343.4343, 'Hello', True, [5, 7]]
#
# nums[0] = 434.32
# nums[3] = False
# print(nums[-1][1])


numbers = [5, 2, 7]
numbers.append(100)
numbers.insert(2, True)

b = [5, 6, 8]
numbers.extend(b)
numbers.sort()
# numbers.reverse() просто переворачивает список
# numbers.pop() удаление последнего элемента или можно выбрать индекс и удалить тот или иной элемент
# numbers.remove(True) удаляет написанный элемент
# numbers.clear() удаление всего списка


# count находит сколько элементов в списке
# len находит сколько всего элементов
print(numbers)

# count находит сколько повторяющихся элементов в списке
# len находит сколько всего элементов
print(numbers)


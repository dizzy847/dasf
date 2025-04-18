# set убирает повторяющиеся множества
# frozenset замораживает список и его никак нельзя изменить

# ФУНКЦИИ
# def test_func():
#     print('Hello', end="")
#     print("!")
#
# test_func()

# def test_func(word):
#     print(word, end="")
#     print("!")
#
# test_func("Hi")
# test_func(5)
# test_func(6.5)

# def summa(a, b):
#     res = a + b
#     print("Result:", res)
#
# summa(5, 7)
# summa("H", "I")

# def summa(a, b):
#     return a + b
#
# res = summa(5, 7)
# print(res)

def minimal(l):
    min_number = l[0]
    for i in l:
        if i < min_number:
            min_number = i
    print(min_number)

nums_1 = [5, 7, 2, 9, 4]
minimal(nums_1)

nums_2 = [5.4, 7.2, 2.3, 2.1, 9.4, 4.2]
minimal(nums_2)

# func = lambda x, y: x * y
# res = func(5, 2)
# print(res) результат 10

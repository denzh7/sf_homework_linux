def greet():
    print("-" * 19)
    print("  Приветсвуем вас  ")
    print("      в игре       ")
    print("  крестики-нолики  ")
    print("-" * 19)
    print(" Для хода введите номер клетки! ")


def show():
    print(f' ___________ \n'
          f'| {cl[7]} | {cl[8]} | {cl[9]} | \n'
          f' _7___8___9_ \n'
          f'| {cl[4]} | {cl[5]} | {cl[6]} | \n'
          f' _4___5___6_ \n'
          f'| {cl[1]} | {cl[2]} | {cl[3]} | \n'
          f' _1___2___3_ \n')


def envir():
    if (cl[1] != ' ' and cl[1] == cl[2] == cl[3] or
        cl[3] != ' ' and cl[3] == cl[6] == cl[9] or
        cl[9] != ' ' and cl[9] == cl[8] == cl[7] or
        cl[7] != ' ' and cl[7] == cl[4] == cl[1] or
        cl[1] != ' ' and cl[1] == cl[5] == cl[9] or
        cl[3] != ' ' and cl[3] == cl[5] == cl[7] or
        cl[4] != ' ' and cl[4] == cl[5] == cl[6] or
        cl[2] != ' ' and cl[2] == cl[5] == cl[8]):
        return True
    else:
        return False


cl = {}
for i in range(1, 10):
    cl[i] = ' '

busy = []
count = 1
greet()
show()
while True:
    if count % 2 == 1:
        numCl = input("Введите номер клетки. Ход крестик: ")
    else:
        numCl = input("Введите номер клетки. Ход нолик: ")

    if not (numCl.isdigit()) or len(numCl) != 1 or 1 > int(numCl) > 9:
        print("Введите (цифру) номер клетки!: ")
        continue

    if numCl in busy:
        print(" Клетка занята! ")
        continue

    busy.append(numCl)

    if count % 2 == 1:
        x = int(numCl)
        cl[x] = 'x'
        if envir():
            show()
            print("      Поздравляю! Выиграл крестик!!! ")
            break
        elif count == 9:
            print(" \n \n        Ничья!!!\n        Победила дружба!!! ")
            break
        else:
            count += 1
            show()
            continue
    else:
        y = int(numCl)
        cl[y] = 'o'
        if envir():
            show()
            print("      Поздравляю! Выиграл нолик!!! ")
            break
        elif count == 9:
            print(" \n \n        Ничья!!!\n        Победила дружба!!! ")
            break
        else:
            count += 1
            show()
            continue

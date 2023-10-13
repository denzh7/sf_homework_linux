import copy
import random

# Константы
DOT_EMPT = "| "
DOT_SHIP = "|П"
DOT_SHOT = "|X"
DOT_MISS = "|#"
STATUS_MISS = 0  # Промахнулся
STATUS_KILL = 1  # Убил
STATUS_SHOT = 2  # Ранил
PLAYER_USER = 0
PLAYER_AI = 1
DIRECT_HOR = 0
DIRECT_VERT = 1


# Выстрел за пределами доски
class ShotOutBoardError(Exception):
    def __init__(self, text):
        self.text = text


# Выстрел по точке МИМО
class ShotOnMissDotError(Exception):
    def __init__(self, text, player):
        self.text = text
        self.player = player


# Выстрел по точке ВЫСТРЕЛЕНО
class ShotOnShotDotError(Exception):
    def __init__(self, text, player):
        self.text = text
        self.player = player


# Нет места для установки корабля
class NoPlaceForShipError(Exception):
    def __init__(self, text):
        self.text = text


# Точки на поле
class ClDot:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # Сравнение на эквивалентность двух точек
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Расчет индекса координаты xy
    def gen_index(self, dim: int):
        return (self.y - 1) * dim + (self.x - 1)


# Корабль
class ClShip:
    def __init__(self, len: int, dot: ClDot, direction: int):
        self.len = len
        self.dot = dot
        self.direction = direction
        self.life = len
        # Сформировать список точек корабля
        self.list_dots_ship = []
        for i in range(self.len):
            if self.direction == DIRECT_HOR:
                dot = ClDot(self.dot.get_x() + i, self.dot.get_y())
            else:
                dot = ClDot(self.dot.get_x(), self.dot.get_y() + i)
            self.list_dots_ship.append(dot)

    # возвращает список всех точек корабля
    def get_list_dots_ship(self):
        return self.list_dots_ship

    # возвращает список всех точек вокруг корабля (могут быть точки вне доски!)
    def contour(self):
        contour_dots = []
        for dot in self.list_dots_ship:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    cur_dot = ClDot(dot.get_x() + i, dot.get_y() + j)
                    if cur_dot not in self.list_dots_ship and cur_dot not in contour_dots:
                        contour_dots.append(cur_dot)
        return contour_dots


# Игровая доска
class ClBoard:
    def __init__(self, dimension: int, hidden: int):
        self.dimension = dimension  # num_cells_user
        self.board = []
        for i in range(self.dimension * self.dimension):
            self.board.append(DOT_EMPT)
        self.list_ships = []
        self.hidden = hidden
        self.alive_ships = 0

    def get_alive_ships(self):
        return self.alive_ships

    def get_dimension(self):
        return self.dimension

    # добавить один корабль на доску
    def add_ship(self, ship: ClShip):
        # Проверка - попадает ли корабль в поле
        for dot_ship in ship.get_list_dots_ship():
            if self.out_of_board(dot_ship):
                raise NoPlaceForShipError(
                    f"Ошибка! Нет места для корабля длиной {ship.len}, x={ship.dot.get_x()}, y={ship.dot.get_y()}")
        # Проверка - не соприкасается ли корабль с другими
        for i in range(0, ship.len + 2):
            for j in range(0, 3):
                if ship.direction == DIRECT_HOR:
                    dot = ClDot(i + ship.dot.get_x() - 1, j + ship.dot.get_y() - 1)
                else:
                    dot = ClDot(j + ship.dot.get_x() - 1, i + ship.dot.get_y() - 1)
                if self.out_of_board(dot):
                    continue
                index = dot.gen_index(self.dimension)
                if self.board[index] != DOT_EMPT:
                    raise NoPlaceForShipError(
                        f"Ошибка! Нет места для корабля длиной {ship.len}, x={ship.dot.get_x()}, y={ship.dot.get_y()}")
        # Установка корабля в доску
        index = ship.dot.gen_index(self.dimension)
        for i in range(0, ship.len):
            if ship.direction == DIRECT_HOR:
                self.board[index + i] = DOT_SHIP
            elif ship.direction == DIRECT_VERT:
                self.board[index + i * self.dimension] = DOT_SHIP
        # Добавить корабль в список
        self.list_ships.append(ship)
        self.alive_ships = self.alive_ships + 1

    # точка вне доски
    def out_of_board(self, dot: ClDot):
        if dot.get_x() > self.dimension:
            return True
        if dot.get_y() > self.dimension:
            return True
        if dot.get_x() < 1:
            return True
        if dot.get_y() < 1:
            return True
        return False

    # Выстрел по доске
    def shot(self, dot: ClDot):
        if self.out_of_board(dot):
            raise ShotOutBoardError(f"Ошибка! Выстрел вне доски: x={dot.get_x()}, y={dot.get_y()}")
        index = dot.gen_index(self.dimension)
        value = self.board[index]
        if value == DOT_EMPT:
            self.board[index] = DOT_MISS
            return STATUS_MISS
        elif value == DOT_SHIP:
            self.board[index] = DOT_SHOT
            for ship in self.list_ships:
                list_dots_ship = ship.get_list_dots_ship()
                dot_belong_to_ship = False
                for ship_dot in list_dots_ship:
                    if dot == ship_dot:
                        dot_belong_to_ship = True
                        break
                if dot_belong_to_ship:
                    ship.life -= 1
                    if ship.life == 0:
                        self.alive_ships -= 1
                        # Автоматически проставить "МИМО" вокруг убитого корабля
                        for cont_dot in ship.contour():
                            if not self.out_of_board(cont_dot):
                                index2 = cont_dot.gen_index(self.dimension)
                                self.board[index2] = DOT_MISS
                        return STATUS_KILL
                    else:
                        return STATUS_SHOT
        elif value == DOT_SHOT:
            raise ShotOnShotDotError(f"Ошибка! Это поле подбито ранее: x={dot.get_x()}, y={dot.get_y()}", PLAYER_USER)
        elif value == DOT_MISS:
            raise ShotOnMissDotError(f"Ошибка! В это поле уже стреляли ранее: x={dot.get_x()}, y={dot.get_y()}",
                                     PLAYER_USER)
        return -1

    # Печать доски
    def print_board(self):
        # Выводим нумерацию колонок
        num_col = ["%2d" % elem for elem in [_ for _ in range(1, self.dimension + 1)]]
        print(f"    {'  '.join(num_col)}")

        j = 0
        # Выводим значения списка list_for_build1 на доску
        for i in range(self.dimension):
            str1 = self.board[j:j + self.dimension]
            str2 = ''.join(str1)
            if self.hidden:
                str2 = str2.replace(DOT_SHIP, DOT_EMPT)  # скрыть все корабли
            str3 = f"{'{:>2}'.format(str(i + 1))} {' '.join(str2)} |"
            j = j + self.dimension
            print(str3)


# Общий класс Игрок
class ClPlayer:
    def __init__(self, dimension):
        self.own_board = ClBoard(dimension, False)
        self.enemy_board = ClBoard(dimension, True)

    # метод, который расставляет рандомно корабли
    def random_board(self):
        too_many_attempts = 0
        for i in range(0, 4):
            len_ = 4 - i
            j = 0
            while j < i + 1:
                x = random.randrange(1, self.own_board.get_dimension() + 1)
                y = random.randrange(1, self.own_board.get_dimension() + 1)
                direction = random.randrange(0, 2)
                dot = ClDot(x, y)
                ship = ClShip(len_, dot, direction)
                try:
                    too_many_attempts += 1
                    self.own_board.add_ship(ship)
                    j = j + 1
                except NoPlaceForShipError as err:
                    # print(err.text) # ДЛЯ ОТЛАДКИ !
                    continue

    # метод пустой, будет переопределён в классах-наследниках
    def ask(self):

        dot = ClDot(0, 0)
        return dot

    # метод, который делает ход в игре
    def move(self):
        # while True:
        try:
            dot = self.ask()
            dot_status = self.enemy_board.shot(dot)
            return dot_status
        except ShotOutBoardError as err:
            print(err.text)
        except ShotOnMissDotError as err:
            if err.player == PLAYER_USER:
                print(err.text)
        except ShotOnShotDotError as err:
            if err.player == PLAYER_USER:
                print(err.text)
        except TypeError as err:
            print("Ошибка! Введено не число!")
        except:
            print("Ошибка ввода!")


# Класс Искусственный интеллект
class ClAI(ClPlayer):
    # метод, который «спрашивает» игрока, в какую клетку он делает выстрел
    def ask(self):
        shot_y = random.randrange(1, self.enemy_board.get_dimension() + 1)
        shot_x = random.randrange(1, self.enemy_board.get_dimension() + 1)
        dot = ClDot(shot_x, shot_y)
        return dot


# Класс Пользователь
class ClUser(ClPlayer):
    # метод, который «спрашивает» игрока, в какую клетку он делает выстрел
    def ask(self):
        shot_x = input(f'{"-" * 50}\n'
                       f'Введите НОМЕР СТОЛБЦА выстрела:  ')
        shot_y = input(f'Введите НОМЕР СТРОКИ выстрела:  ')
        if shot_x.isdigit() and shot_y.isdigit():
            dot = ClDot(int(shot_x), int(shot_y))
        else:
            raise TypeError
        return dot


# Класс Игра
class Game:
    def __init__(self, dimension):
        self.user = ClUser(dimension)
        self.ai = ClAI(dimension)

    # Приветствие пользователя
    @staticmethod
    def greet():
        # метод, который в консоли приветствует пользователя и рассказывает о формате ввода.
        print((f'{"-" * 20}\n'
               f'  Приветствуем Вас  \n'
               f'      в игре       \n'
               f'    Морской Бой    \n'
               f'{"-" * 20}'))
        while True:
            num_cells_user = input(f'Введите количество клеток ширины игрового поля от 10 до 15: ')
            if num_cells_user.isdigit() and int(num_cells_user) in range(10, 16):
                break
            else:
                print("Вы не выбрали ни один из предложенных вариантов, попробуйте ещё раз ")
        return int(num_cells_user)

    # Прощание с пользователем
    def farewell(self):
        print((f'{"-" * 20}\n'
               f'   Ждём Вас снова  \n '
               f'      в игре       \n'
               f'    Морской Бой    \n'
               f'{"-" * 20}'))

    # Вывести на печать обе доски
    def print_all(self):
        print(f"Доска пользователя")
        self.ai.enemy_board.print_board()
        print(f"Доска искусственного интеллекта")
        self.user.enemy_board.print_board()

    # Игровой цикл
    def loop(self):
        user_win = False
        while True:
            # Ход игрока
            while True:
                self.print_all()
                print(f"{'-' * 50}=== ВАШ ХОД ===")
                dot_status = self.user.move()
                num_ai_alive_ships = self.user.enemy_board.get_alive_ships()
                if dot_status == STATUS_KILL and num_ai_alive_ships == 0:
                    user_win = True
                    break
                if dot_status == STATUS_KILL:
                    print(f"{'-' * 50} Поздравляем! Корабль противника убит! Сделайте ещё один выстрел!")
                if dot_status == STATUS_SHOT:
                    print(f"{'-' * 50} Корабль противника ранен! Сделайте ещё один выстрел!")
                if dot_status == STATUS_MISS:
                    print(f"{'-' * 50}Эх...мимо!")
                    break

            # Условие 1 конца игры
            if num_ai_alive_ships == 0:
                break

            # Ход ИИ
            while True:
                print(f"{'-' * 50}=== ХОД ИИ ===")
                dot_status = self.ai.move()
                num_user_alive_ships = self.user.enemy_board.get_alive_ships()
                if dot_status == STATUS_KILL and num_user_alive_ships == 0:
                    user_win = False
                    break
                if dot_status == STATUS_KILL:
                    print(f"{'-' * 50} Сори(  Ваш корабль убит.")
                if dot_status == STATUS_SHOT:
                    print(f"{'-' * 50} Упс(   Ваш корабль ранен.")
                if dot_status == STATUS_MISS:
                    print(f"{'-' * 50} Ура! ИИ промахнулся.")
                    break

            # Условие 2 конца игры
            if num_user_alive_ships == 0:
                break

        if user_win:
            print(f"Поздравляем!!!\n"
                  f"Вы победили!")
        else:
            print(f"Вы проиграли.\n"
                  f"Победил искусственный интеллект!")

    # Начало игры
    def start(self):
        self.user.random_board()
        self.ai.random_board()
        self.user.enemy_board = copy.deepcopy(self.ai.own_board)
        self.user.enemy_board.hidden = True
        self.ai.enemy_board = copy.deepcopy(self.user.own_board)
        self.ai.enemy_board.hidden = False
        self.loop()
        self.farewell()


# _________ ОСНОВНАЯ ПРОГРАММА ___________

num_cells_user = Game.greet()
Game_1 = Game(num_cells_user)
Game_1.start()

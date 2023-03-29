from random import randint, choice

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

class Ship:
    def __init__(self, bow, length, orient):
        self.bow = bow
        self.length = length
        self.orient = orient
        self.lives = length
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            if self.orient == 'g':
                a = self.bow.x
                b = self.bow.y + i
                ship_dots.append(Dot(a, b))
            if self.orient == 'v':
                a = self.bow.x + i
                b = self.bow.y
                ship_dots.append(Dot(a, b))

        return ship_dots
    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.result = False

    def display(self):
        display = []
        display += ['  | 1 | 2 | 3 | 4 | 5 | 6 |']
        for i, row in enumerate(self.field):
            display.append(f"{i + 1} | " + " | ".join(row) + " |")

        if self.hid:
            for i in range(1, self.size+1):
                display[i] = display[i].replace("■", "O")
        return display

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)
    def shot(self, d):
        if self.out(d):
            if self.hid:
                raise BoardOutException()
            if not self.hid:
                raise BoardException()

        if d in self.busy:
            if self.hid:
                raise BoardUsedException()
            if not self.hid:
                raise BoardException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    self.result = None
                    return self.result
                else:
                    self.result = ship.lives
                    return self.result

        self.field[d.x][d.y] = "."
        self.result = False
        return self.result
    def print_result(self):
        if self.result is None:
            print("Корабль уничтожен!")
        elif self.result:
            print("Корабль ранен!")
        else:
            print("Мимо!")

    def begin(self):
        self.busy = []
    def defeat(self):
        return self.count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
        self.lives_injure = False
        self.dot_injure = False

class AI(Player):
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
            except BoardException:
                pass
            else:
                print(f"Ход компьютера: {target.x + 1} {target.y + 1}")
                self.enemy.print_result()
                if repeat:
                    self.lives_injure = repeat
                    self.dot_injure = target
                if repeat is None:
                    self.lives_injure = False
                    self.dot_injure = False
                return repeat
    def ask(self):
        if self.lives_injure:
            cho = choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            d = Dot(self.dot_injure.x+cho[0], self.dot_injure.y+cho[1])
        else:
            d = Dot(randint(0, 5), randint(0, 5))
        return d

class User(Player):
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
            except BoardException as e:
                print(e)
            else:
                self.enemy.print_result()
                return repeat

    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)

class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size = self.size)
        attempts = 0
        for i in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, choice('vg'))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("------------------------------------------------------------------")
        print("              Приветсвуем вас в игре морской бой! ")
        print("------------------------------------------------------------------")
        print("     Формат ввода: x y (x - номер строки, y - номер столбца)")

    def print_boards(self):
        us_board = Board.display(self.us.board)
        ai_board = Board.display(self.ai.board)
        print("-" * 66)
        print("     Доска пользователя:                    Доска компьютера:")
        for i in range(len(us_board)):
            print(us_board[i], '          ', ai_board[i])
        print("-" * 66)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("Вы выиграли!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
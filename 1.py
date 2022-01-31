#!/usr/bin/env python3

import pygame
import os
import sys
import time


def draw_text(screen, my_text, kol=(0, 0, 0), ras=(15, 15)):
    font = pygame.font.Font(None, 75)
    text = font.render(my_text, True, kol)
    screen.blit(text, ras)


def nachalo():
    global screen, startx, starty, all_sprites, tiles_group, player_group, fin_group, \
        sloi_lab, my_index, tile_width, tile_height, level_x, level_y, level_in_txt, \
        player, vse_yrovne, index_yrovna, vol, dark_group

    if index_yrovna < len(vse_yrovne):
        screen.fill((0, 0, 0))

        pygame.mixer.music.load(load_music('фон_музыка.mp3'))
        pygame.mixer.music.play(-1)

        pygame.display.flip()
        startx, starty = None, None
        all_sprites = pygame.sprite.Group()
        tiles_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()
        fin_group = pygame.sprite.Group()
        dark_group = pygame.sprite.Group()

        sloi_lab = vse_yrovne[index_yrovna]
        my_index = 0

        tile_width = tile_height = 50
        level_x, level_y, startx, starty = generate_level(load_level(sloi_lab[my_index]))

        level_in_txt = load_level(sloi_lab[my_index])
        # ----------------
        player = pygame.sprite.Sprite(all_sprites)
        player.image = player_image
        player.rect = player.image.get_rect()
        all_sprites.add(player)
        player_group.add(player)
        startx, starty = starty, startx
        player.rect.top += startx * tile_width
        player.rect.left += starty * tile_height

        dark = pygame.sprite.Sprite(dark_group)
        dark.image = Board.load_image('MainDark.png', None, (width, height))
        dark.rect = dark.image.get_rect()
        dark_group.add(dark)
        index_yrovna += 1

        with open("data/" + 'index_yrovna.txt', 'w') as f:
            f.write(str(index_yrovna))

        pygame.display.flip()

    else:
        screen.fill((0, 0, 0))

        pygame.mixer.pause()
        pygame.mixer.music.load(load_music('победа.wav'))
        pygame.mixer.music.play(-1)

        zastavka_fun('maxresdefault.jpg')

        pygame.display.flip()

        with open("data/" + 'index_yrovna.txt', 'w') as f:
            f.write(str(1))

        while True:  # главный игровой цикл
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    menu()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    zastavka_fun('пасхалка.jpg')
                    time.sleep(10)
                    zastavka_fun('maxresdefault.jpg')


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.tile_type = tile_type
        if self.tile_type == 'tyr':
            self.pos_tyr = (pos_x, pos_y)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group) and self.tile_type == 'finish':
            time.sleep(0.5)
            nachalo()

        if pygame.sprite.spritecollideany(self, player_group) and self.tile_type == 'tyr':
            global index_yrovna

            screen.fill((0, 0, 0))

            pygame.mixer.pause()
            pygame.mixer.music.load(load_music('смерть.mp3'))
            pygame.mixer.music.play(-1)

            zastavka_fun('смерть.jpg', 2)

            pygame.mixer.pause()

            index_yrovna -= 1
            nachalo()

        if pygame.sprite.spritecollideany(self, player_group) and \
                (self.tile_type == 'tyr1' or self.tile_type == 'tyr2'):
            screen.fill((0, 0, 0))

            pygame.mixer.pause()
            pygame.mixer.music.load(load_music('смерть.mp3'))
            pygame.mixer.music.play(-1)

            zastavka_fun('смерть.jpg', 2)

            pygame.mixer.pause()

            index_yrovna -= 1
            nachalo()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                posx, posy = x, y
            elif level[y][x] == '!':
                Tile('empty', x, y)
                Tile('finish', x, y)
            elif level[y][x] == '$':
                Tile('empty', x, y)
                Tile('tyr', x, y)
            elif level[y][x] == '-':
                Tile('empty', x, y)
                Tile('tyr1', x, y)
            elif level[y][x] == '|':
                Tile('empty', x, y)
                Tile('tyr2', x, y)

    # вернем игрока, а также размер поля в клетках
    if not (startx is None):
        posx, posy = startx, starty

    return x, y, posx, posy


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def load_image(name, colorkey=None, fon=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()

        if colorkey is not None:
            image = pygame.image.load(fullname).convert()
            transColor = image.get_at((0, 0))
            image.set_colorkey(transColor)
            image = pygame.image.load(fullname).convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = pygame.image.load(fullname)
            image = image.convert_alpha()

        if fon is None:
            image = pygame.transform.scale(image, (50, 50))

        else:
            image = pygame.transform.scale(image, fon)

        return image


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def sloi():
    global my_index, startx, starty, level_in_txt
    global all_sprites, tiles_group
    if my_index == len(sloi_lab) - 1:
        my_index = 0
    else:
        my_index += 1

    level_in_txt = load_level(sloi_lab[my_index])
    if len(level_in_txt) > startx and len(level_in_txt[startx]) > starty and level_in_txt[startx][starty] != '#':
        screen.fill((0, 0, 0))

        all_sprites = pygame.sprite.Group()
        tiles_group = pygame.sprite.Group()

        level_x, level_y, startx, starty = generate_level(load_level(sloi_lab[my_index]))

        player.image = player_image
        player.rect = player.image.get_rect()
        all_sprites.add(player)
        player_group.add(player)
        player.rect.top += startx * tile_width
        player.rect.left += starty * tile_height

        all_sprites.update()
    else:
        if my_index == 0:
            my_index = len(sloi_lab) - 1
        else:
            my_index -= 1

        level_in_txt = load_level(sloi_lab[my_index])


def load_music(name):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    return fullname


def pravila():
    running = True
    flag_prav = 0

    while running:  # главный игровой цикл
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEMOTION:
                if prav_x <= event.pos[0] <= prav_s1 and prav_y <= event.pos[1] <= prav_s2:
                    prav_knop.image = Board.load_image('AcceptRulesHover.png', None, (raz_prav1, raz_prav2))
                    flag_prav = 1

                else:
                    prav_knop.image = Board.load_image('AcceptRules.png', None, (raz_prav1, raz_prav2))

            if flag_prav == 1 and event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        prav_group.draw(screen)
        pygame.display.flip()


def menu():
    global vol, index_yrovna

    flag = 0

    running = True

    while running:  # главный игровой цикл
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEMOTION:
                if x1Firstbtn <= event.pos[0] <= x2Firstbtn and y1Firstbtn <= event.pos[1] <= y2Firstbtn:
                    flag = 1
                    knopka1.image = Board.load_image('NewGameHover.png', None, (size1FirstBtn, size2FirstBtn))

                elif x1Secbtn <= event.pos[0] <= x2Secbtn and y1Secbtn <= event.pos[1] <= y2Secbtn:
                    flag = 2
                    knopka2.image = Board.load_image('RulesHover.png', None, (size1SecBtn, size2SecBtn))

                elif x1Thirdbtn <= event.pos[0] <= x2Thirdbtn and y1Thirdbtn <= event.pos[1] <= y2Thirdbtn:
                    flag = 3
                    knopka3.image = Board.load_image('ExitHover.png', None, (size1ThirdBtn, size2ThirdBtn))

                elif x1Forthbtn <= event.pos[0] <= x2Forthbtn and y1Forthbtn <= event.pos[1] <= y2Forthbtn:
                    flag = 4
                    knopka4.image = Board.load_image('VolumeMinus.png', None, (size1ForthBtn + 5, size2ForthBtn + 5))
                elif x1Fivebtn <= event.pos[0] <= x2Fivebtn and y1Fivebtn <= event.pos[1] <= y2Fivebtn:
                    flag = 5
                    knopka5.image = Board.load_image('VolumePlus.png', None, (size1FiveBtn + 5, size2FiveBtn + 5))

                else:
                    if flag == 1:
                        knopka1.image = Board.load_image('NewGame.png', None, (size1FirstBtn, size2FirstBtn))
                    elif flag == 2:
                        knopka2.image = Board.load_image('Rules.png', None, (size1SecBtn, size2SecBtn))
                    elif flag == 3:
                        knopka3.image = Board.load_image('Exit.png', None, (size1ThirdBtn, size2ThirdBtn))
                    elif flag == 4:
                        knopka4.image = Board.load_image('VolumeMinus.png', None, (size1ForthBtn, size2ForthBtn))
                    elif flag == 5:
                        knopka5.image = Board.load_image('VolumePlus.png', None, (size1FiveBtn, size2FiveBtn))
                    flag = 0
            if event.type == pygame.MOUSEBUTTONDOWN and flag != 0:
                if flag == 1:
                    index_yrovna = 0
                    nachalo()
                    running = False

                if flag == 2:
                    pravila()

                if flag == 3:
                    sys.exit()

                if flag == 4:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)

                if flag == 5:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)

        knopks_group.update()
        knopks_group.draw(screen)
        pygame.display.flip()


def zastavka_fun(name, time_sleep=None):
    running = True
    zastavka = pygame.sprite.Group()
    zast = pygame.sprite.Sprite(zastavka)
    zast.image = Board.load_image(name, None, (width, height))
    zast.rect = zast.image.get_rect()
    zastavka.add(zast)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    zastavka.draw(screen)
    pygame.display.flip()
    if not (time_sleep is None):
        time.sleep(time_sleep)
    running = False


if __name__ == '__main__':

    pygame.mixer.pre_init(44100, -16, 1, 512)

    pygame.init()
    size = width, height = 1920, 1080
    screen = pygame.display.set_mode(size)
    pygame.display.flip()
    fps = 15  # количество кадров в секунду
    clock = pygame.time.Clock()
    running = True
    tile_images = {
        'wall': Board.load_image('fonn.jpg'),
        'empty': Board.load_image('14.jpg'),
        'finish': Board.load_image('bitkoin.jpg'),
        'tyr': Board.load_image('чел.jpg'),
        'tyr1': Board.load_image('booomb.jpg'),
        'tyr2': Board.load_image('booomb.jpg')
    }

    player_image = Board.load_image('skel2.png')

    # ============================================
    knopks_group = pygame.sprite.Group()

    zast_menu = pygame.sprite.Sprite(knopks_group)
    zast_menu.image = Board.load_image('фон_меню_вигре(1).png', None, (width, height))
    zast_menu.rect = zast_menu.image.get_rect()
    knopks_group.add(zast_menu)

    size1FirstBtn, size2FirstBtn = 500, 100
    x1Firstbtn, y1Firstbtn = 1280, 100
    x2Firstbtn, y2Firstbtn = x1Firstbtn + size1FirstBtn, y1Firstbtn + size2FirstBtn

    knopka1 = pygame.sprite.Sprite(knopks_group)
    knopka1.image = Board.load_image('NewGame.png', None, (size1FirstBtn, size2FirstBtn))
    knopka1.rect = knopka1.image.get_rect()
    knopks_group.add(knopka1)
    knopka1.rect.top += y1Firstbtn
    knopka1.rect.left += x1Firstbtn

    # -----------

    size1SecBtn, size2SecBtn = 500, 100
    x1Secbtn, y1Secbtn = 1280, 300
    x2Secbtn, y2Secbtn = x1Secbtn + size1SecBtn, y1Secbtn + size2SecBtn

    knopka2 = pygame.sprite.Sprite(knopks_group)
    knopka2.image = Board.load_image('Rules.png', None, (size1SecBtn, size2SecBtn))
    knopka2.rect = knopka2.image.get_rect()
    knopks_group.add(knopka2)
    knopka2.rect.top += y1Secbtn
    knopka2.rect.left += x1Secbtn
    # -----------

    size1ThirdBtn, size2ThirdBtn = 500, 100
    x1Thirdbtn, y1Thirdbtn = 1280, 500
    x2Thirdbtn, y2Thirdbtn = x1Thirdbtn + size1ThirdBtn, y1Thirdbtn + size2ThirdBtn

    knopka3 = pygame.sprite.Sprite(knopks_group)
    knopka3.image = Board.load_image('Exit.png', None, (size1ThirdBtn, size2ThirdBtn))
    knopka3.rect = knopka3.image.get_rect()
    knopks_group.add(knopka3)
    knopka3.rect.top += y1Thirdbtn
    knopka3.rect.left += x1Thirdbtn

    # ----------
    size1ForthBtn, size2ForthBtn = 100, 100
    x1Forthbtn, y1Forthbtn = 1280, 800
    x2Forthbtn, y2Forthbtn = x1Forthbtn + size1ForthBtn, y1Forthbtn + size2ForthBtn

    knopka4 = pygame.sprite.Sprite(knopks_group)
    knopka4.image = Board.load_image('VolumeMinus.png', None, (size1ForthBtn, size2ForthBtn))
    knopka4.rect = knopka4.image.get_rect()
    knopks_group.add(knopka4)
    knopka4.rect.top += y1Forthbtn
    knopka4.rect.left += x1Forthbtn
    # ----------
    size1FiveBtn, size2FiveBtn = 100, 100
    x1Fivebtn, y1Fivebtn = 1680, 800
    x2Fivebtn, y2Fivebtn = x1Fivebtn + size1FiveBtn, y1Fivebtn + size2FiveBtn

    knopka5 = pygame.sprite.Sprite(knopks_group)
    knopka5.image = Board.load_image('VolumePlus.png', None, (size1FiveBtn, size2FiveBtn))
    knopka5.rect = knopka5.image.get_rect()
    knopks_group.add(knopka5)
    knopka5.rect.top += y1Fivebtn
    knopka5.rect.left += x1Fivebtn

    prav_group = pygame.sprite.Group()

    prav = pygame.sprite.Sprite(prav_group)
    prav.image = Board.load_image('правила.jpg', None, (int(width * 0.85), int(height * 0.85)))
    prav.rect = prav.image.get_rect()
    prav_group.add(prav)


    prav_x, prav_y = 800, 900#900
    raz_prav1, raz_prav2 = 350, 100
    prav_s1, prav_s2 = prav_x + raz_prav1, prav_y + raz_prav2
    prav_knop = pygame.sprite.Sprite(prav_group)
    prav_knop.image = Board.load_image('Rules.png', None, (raz_prav1, raz_prav2))
    prav_knop.rect = prav_knop.image.get_rect()
    prav_group.add(prav_knop)
    prav_knop.rect.top += prav_y
    prav_knop.rect.left += prav_x

    vse_yrovne = [['1.txt', '2.txt'],
                  ['3.txt', '4.txt', '5.txt'],
                  ['hardLvl.txt', 'pole_is_bomb.txt'],
                  ['11.txt', '12.txt', '13.txt'],
                  ['6.txt', '7.txt', '8.txt', '9.txt', '10.txt']]

    with open("data/" + 'index_yrovna.txt', 'r') as f:
        index_yrovna = int(f.readline())
    index_yrovna -= 1

    camera = Camera()

    p = pygame.mixer.Sound(load_music('сердце.wav'))  # переключение между слоями

    s = pygame.mixer.Sound(load_music('шаг.wav'))  # шаги

    t = pygame.mixer.Sound(load_music('сердце.wav'))  # стук сердца

    vol = 1.0

    pygame.mixer.music.load(load_music('смерть.mp3'))
    pygame.mixer.music.play(-1)

    zastavka_fun('Header.png', 3)

    pygame.mixer.pause()

    running = True

    nachalo()

    while running:  # главный игровой цикл
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    p.play()
                    sloi()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                index_yrovna -= 1
                nachalo()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                if startx != 0 and level_in_txt[startx - 1][starty] != '#':
                    player.rect.top -= tile_width
                    startx -= 1
                    player_group.update()
                    player_image = Board.load_image('skel1.png')
                    s.play()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                if startx != len(level_in_txt) - 1 and level_in_txt[startx + 1][starty] != '#':
                    player.rect.top += tile_width
                    startx += 1
                    player_image = Board.load_image('skel2.png')
                    s.play()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                if starty != 0 and level_in_txt[startx][starty - 1] != '#':
                    player.rect.left -= tile_height
                    starty -= 1
                    player_image = Board.load_image('skel3.png')
                    s.play()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                if starty != len(level_in_txt[0]) - 1 and level_in_txt[startx][starty + 1] != '#':
                    player.rect.left += tile_height
                    starty += 1
                    player_image = Board.load_image('skel4.png')
                    s.play()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu()

            player.image = player_image

            all_sprites.update()

        # изменяем ракурс камеры
        camera.update(player);
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)

        all_sprites.update()
        all_sprites.draw(screen)
        fin_group.draw(screen)
        player_group.draw(screen)
        dark_group.draw(screen)

        draw_text(screen, str(index_yrovna) + '/' + str(len(vse_yrovne)), (255, 200, 200), (15, 15))
        draw_text(screen, str(my_index + 1) + '/' + str(len(sloi_lab)), (200, 200, 200), (15, 60))

        pygame.display.flip()
        clock.tick(fps)
pygame.quit()

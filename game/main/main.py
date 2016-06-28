import pygame
import sys
from pygame import *
from SpriteStripAnim import SpriteStripAnim
from pytmx.util_pygame import load_pygame


class Player(object):
    def __init__(self, o_screen):
        self.x = 200
        self.y = 300
        self.move_by = 2
        self.frames = 10
        self.strips = [
            SpriteStripAnim('Actor1.png', (0, 0, 32, 32), 3, -1, True, self.frames),
            SpriteStripAnim('Actor1.png', (0, 32, 32, 32), 3, -1, True, self.frames),
            SpriteStripAnim('Actor1.png', (0, 64, 32, 32), 3, -1, True, self.frames),
            SpriteStripAnim('Actor1.png', (0, 96, 32, 32), 3, -1, True, self.frames),
        ]
        self.anim_pos_x = 0
        self.anim_max = 2
        self.n = 0
        self.strips[self.n].iter()
        self.img = self.strips[self.n].next()
        self.empty = {}
        self.update(0, 0, "down", o_screen, self.empty)
        self.pos_x = 0
        self.pos_y = 0
        self.dir_move = {}
        self.pressed_up = False
        self.pressed_down = False
        self.pressed_left = False
        self.pressed_right = False
        self.direction = {
            "UP": "up",
            "DOWN": "down",
            "LEFT": "left",
            "RIGHT": "right"
        }

    def handle_event(self, events):
        return_val = {}
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.pressed_left = True
                elif event.key == pygame.K_RIGHT:
                    self.pressed_right = True
                elif event.key == pygame.K_UP:
                    self.pressed_up = True
                elif event.key == pygame.K_DOWN:
                    self.pressed_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.pressed_left = False
                elif event.key == pygame.K_RIGHT:
                    self.pressed_right = False
                elif event.key == pygame.K_UP:
                    self.pressed_up = False
                elif event.key == pygame.K_DOWN:
                    self.pressed_down = False

        if self.pressed_left:
            self.pos_x = self.move_by
            self.pos_y = 0
            self.dir_move = self.direction["LEFT"]
        if self.pressed_right:
            self.pos_x = self.move_by
            self.pos_y = 0
            self.dir_move = self.direction["RIGHT"]
        if self.pressed_up:
            self.pos_x = 0
            self.pos_y = self.move_by
            self.dir_move = self.direction["UP"]
        if self.pressed_down:
            self.pos_x = 0
            self.pos_y = self.move_by
            self.dir_move = self.direction["DOWN"]
        if not self.pressed_left and not self.pressed_right and not self.pressed_up and not self.pressed_down:
            self.pos_x = 0
            self.pos_y = 0

        return_val.update({"pos_x": self.pos_x, "pos_y": self.pos_y, "dir_move": self.dir_move})
        return return_val

    def update(self, pos_x2, pos_y2, dir_move2, o_screen, o_wall):
        #Testing
        player_rect = pygame.Rect(self.x, self.y, 32, 32)
        collision = False
        for obj_img in o_wall:
            new_x = obj_img.rect.x
            new_y = obj_img.rect.y
            obj_2 = pygame.Rect(new_x * 32, new_y * 32, 32, 32)
            if player_rect.colliderect(obj_2):
                collision = True
                break

        if pos_x2 != 0 and pos_y2 == 0:
            if dir_move2 == "right":
                if not collision:
                    self.x += pos_x2
                    self.n = 2
                else:
                    self.x -= 5
            elif dir_move2 == "left":
                if not collision:
                    self.x -= pos_x2
                    self.n = 1
                else:
                    self.x += 5
        elif pos_y2 != 0 and pos_x2 == 0:
            if dir_move2 == "down":
                if not collision:
                    self.y += pos_y2
                    self.n = 0
                else:
                    self.y -= 5
            elif dir_move2 == "up":
                if not collision:
                    self.y -= pos_y2
                    self.n = 3
                else:
                    self.y += 5

        o_screen.blit(self.strips[self.n].next(), (self.x, self.y))


class WorldMap(object):
    def __init__(self, surface, filename):
        self.__surface = surface
        self.__tmx_data = load_pygame(filename)

        if self.__tmx_data.background_color:
            self.__surface.fill(pygame.Color(self.__tmx_data.background_color))

    def add_layer_to_surface(self, layer_name):
        new_layer = self.__tmx_data.get_layer_by_name(layer_name)
        for x, y, image in new_layer.tiles():
            self.__surface.blit(image, (x * self.__tmx_data.tilewidth, y * self.__tmx_data.tileheight))

    def make_blockers(self, blocker_name):
        """
        Make the collideable blockers the player can collide with.
        """
        blockers = pygame.sprite.Group()

        new_layer = self.__tmx_data.get_layer_by_name(blocker_name)
        for x, y, image in new_layer.tiles():
            blocker = pygame.sprite.Sprite()
            blocker.state = None
            blocker.rect = pygame.Rect(x, y, 32, 32)
            blockers.add(blocker)

        return blockers


class Main(object):

    def __init__(self):
        self.h = 640
        self.w = 640
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()
        self.player1 = Player(self.screen)
        self.world1 = WorldMap(self.screen, "Forest1.tmx")
        self.wall = {}

    def start(self):
        while 1:
            self.screen.fill((0, 0, 0))
            self.clock.tick(60)
            return_val2 = self.player1.handle_event(pygame.event.get())
            self.world1.add_layer_to_surface("Grass")
            self.world1.add_layer_to_surface("Path")
            self.world1.add_layer_to_surface("TreeBase")
            self.world1.add_layer_to_surface("pathObjects")
            #self.world1.add_layer_to_surface("Collision")
            self.wall = self.world1.make_blockers("Collision")
            self.player1.update(return_val2["pos_x"], return_val2["pos_y"], return_val2["dir_move"], self.screen, self.wall)
            self.world1.add_layer_to_surface("TreeTops")
            pygame.display.update()

Main().start()

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
        self.pos_x = 0
        self.pos_y = 0
        self.dir_move = {}
        self.pressed_up = False
        self.pressed_down = False
        self.pressed_left = False
        self.pressed_right = False
        self.player_rect = pygame.Rect(self.x, self.y, 32, 32)
        self.surface = o_screen

    def move(self, dx, dy, o_wall):

        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0, o_wall)
        if dy != 0:
            self.move_single_axis(0, dy, o_wall)

    def move_single_axis(self, dx, dy, o_wall):

        # Move the rect
        self.player_rect.x += dx
        self.player_rect.y += dy

        # If you collide with a wall, move out based on velocity
        for wall in o_wall:
            new_x = wall.rect.x
            new_y = wall.rect.y
            obj_2 = pygame.Rect(new_x * 32, new_y * 32, 32, 32)
            if self.player_rect.colliderect(obj_2):
                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.player_rect.right = obj_2.left
                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.player_rect.left = obj_2.right
                if dy > 0:  # Moving down; Hit the top side of the wall
                    self.player_rect.bottom = obj_2.top
                if dy < 0:  # Moving up; Hit the bottom side of the wall
                    self.player_rect.top = obj_2.bottom
            # Used for testing
            pygame.draw.rect(self.surface, (255, 0, 0), obj_2, 3)
            pygame.draw.rect(self.surface, (0, 255, 0), self.player_rect, 3)

    def handle_event(self, events, o_wall):
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
            self.n = 1
            self.pos_x = -self.move_by
            self.pos_y = 0
        if self.pressed_right:
            self.n = 2
            self.pos_x = self.move_by
            self.pos_y = 0
        if self.pressed_up:
            self.n = 3
            self.pos_x = 0
            self.pos_y = -self.move_by
        if self.pressed_down:
            self.n = 0
            self.pos_x = 0
            self.pos_y = self.move_by
        if not self.pressed_left and not self.pressed_right and not self.pressed_up and not self.pressed_down:
            self.pos_x = 0
            self.pos_y = 0

        self.move(self.pos_x, self.pos_y, o_wall)
        self.surface.blit(self.strips[self.n].next(), (self.player_rect.x, self.player_rect.y))


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
            self.world1.add_layer_to_surface("Grass")
            self.world1.add_layer_to_surface("Path")
            self.world1.add_layer_to_surface("TreeBase")
            self.world1.add_layer_to_surface("pathObjects")
            self.wall = self.world1.make_blockers("Collision")
            self.player1.handle_event(pygame.event.get(), self.wall)
            self.world1.add_layer_to_surface("TreeTops")
            pygame.display.update()

Main().start()

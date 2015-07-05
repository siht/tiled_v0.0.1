'''most of this script is based on scripts of sjbrown
http://ezide.com/games/writing-games.html'''
from __future__ import print_function
from graphics import SectorSprite, CharactorSprite
from events import *
from patterns import AbsListener
import pygame
import preferences as pref
import pytweener

class DummyClass: pass

class MainView(AbsListener):
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.registerListener(self)
        pygame.init()
        self.window = pygame.display.set_mode(pref.WINDOW_SIZE)
        pygame.display.set_caption('my first game mvc')
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill(pref.BLACK)
        self.back_sprites = pygame.sprite.LayeredDirty()
        pygame.display.flip()
        self.front_sprites = pygame.sprite.LayeredDirty()
        self.dirty_rects = None
        self.tweener = pytweener.Tweener()

    def showMap(self, game_map): # improve this method
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()
        size = pref.SIZE_TILE
        position_rect = pygame.Rect((0, size, size, size))

        i = 0
        for sector in game_map.sectors:
            if i < pref.SECTOR_WIDTH:
                position_rect = position_rect.move(size,0)
            else:
                i = 0
                position_rect = position_rect.move(-(size*(pref.SECTOR_WIDTH-1)), size)
            i += 1
            new_sprite = SectorSprite(sector, self.back_sprites)
            new_sprite.rect = position_rect
            self.background.blit(new_sprite.image, new_sprite.rect)
            new_sprite = None

    def getCharactorSprite(self, charactor):
        #there will be only one
        for s in self.front_sprites:
            return s
        return None

    def getSectorSprite(self, sector):
        for s in self.back_sprites:
            if hasattr(s, "sector") and s.sector == sector:
                return s

    def putCharactor(self, charactor):
        sector = charactor.sector
        charactor_sprite = CharactorSprite(self.ev_manager, charactor, self.front_sprites)
        sector_sprite = self.getSectorSprite(sector)
        charactor_sprite.rect.midbottom = sector_sprite.rect.midbottom

    def showCharactor(self, charactor):
        sector = charactor.sector
        charactor_sprite = self.getCharactorSprite(charactor)
        sector_sprite = self.getSectorSprite(sector)
        charactor_sprite.rect.midbottom = sector_sprite.rect.midbottom

    def moveCharactor(self, charactor, direction):
        origin = self.getCharactorSprite(charactor.sector)
        x, y = origin.rect.topleft
        self.__coord = DummyClass()
        self.__coord.sp = self.getCharactorSprite(charactor)
        self.__coord.x, self.__coord.y = x, y
        if direction == pref.DIRECTION_UP:
            y -= pref.SIZE_TILE
        elif direction == pref.DIRECTION_DOWN:
            y += pref.SIZE_TILE
        elif direction == pref.DIRECTION_LEFT:
            x -= pref.SIZE_TILE
        elif direction == pref.DIRECTION_RIGHT:
            x += pref.SIZE_TILE
        delay = -(pref.MOVING_TIME_SECONDS/2)
        self.tweener.addTween(self.__coord,
                              x=x,
                              y=y,
                              tweenTime=pref.MOVING_TIME_SECONDS+delay,
                              tweenType=pytweener.Easing.Linear.easeNone)

    def draw(self):
        self.back_sprites.clear(self.window, self.background)
        self.front_sprites.clear(self.window, self.background)

        dirty_rects1 = self.back_sprites.draw(self.window)
        dirty_rects2 = self.front_sprites.draw(self.window)
        self.dirty_rects = dirty_rects1 + dirty_rects2

    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.tweener.hasTweens():
                self.tweener.update(event.aps / 1000.0)
                x, y = self.__coord.x, self.__coord.y
                rect = self.__coord.sp.image.get_rect()
                self.__coord.sp.rect = rect.move(x, y)
                self.__coord.sp.dirty = 1
            self.draw()
            if self.dirty_rects:
                pygame.display.update(self.dirty_rects)
                self.dirty_rects = []
        elif isinstance(event, MapBuiltEvent):
            game_map = event.map
            self.showMap(game_map)
        elif isinstance(event, CharactorPlaceEvent):
            self.putCharactor(event.charactor)
        elif isinstance(event, CharactorMoveEvent):
            self.showCharactor(event.charactor)
        elif isinstance(event, IWillMoveToEvent):
            self.moveCharactor(event.charactor, event.direction)

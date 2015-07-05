from __future__ import print_function
from patterns import FlyWeight, typewrapper, AbsListener
from utils import load_img, Surfaces
from preferences import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT
from preferences import MOVING_TIME_SECONDS as MTS
from preferences import SIZE_TILE
from events import *
import pygame
import time

@typewrapper(pygame.surface.Surface, '_surf')
class SurfaceImage(object):
    '''wrapper of a basic Surface of pygame only for images'''
    __metaclass__ = FlyWeight
    def __init__(self, path):
        self._surf = load_img(path)

    wrap = property(lambda self: self._surf)

class SectorSprite(pygame.sprite.DirtySprite):
    '''sprite of a void sector'''
    def __init__(self, sector, group=None):
        pygame.sprite.DirtySprite.__init__(self, group)
        grounds = SurfaceImage('Tileset- ground.png')
        default_ground = Surfaces.listSurface(grounds, (13, 8))[40]
        self.image = Surfaces.scale(default_ground, (SIZE_TILE, SIZE_TILE))
        self.rect = self.image.get_rect()
        self.sector = sector

class CharactorSprite(pygame.sprite.DirtySprite, AbsListener):
    '''sprite of the main character'''
    STAND = 1

    def __init__(self, ev_manager, charactor, group = None):
        pygame.sprite.DirtySprite.__init__(self, group)

        self.ev_manager = ev_manager
        self.ev_manager.registerListener(self)

        self.charactor = charactor

        aux = Surfaces.listSurface(SurfaceImage('walk_front2.png'), (3,1))
        self.images = {DIRECTION_DOWN : aux}
        aux = Surfaces.listSurface(SurfaceImage('walk_sleft2.png'), (3,1))
        self.images.update({DIRECTION_LEFT : aux})
        aux = Surfaces.listSurface(SurfaceImage('walk_sright2.png'), (3,1))
        self.images.update({DIRECTION_RIGHT : aux})
        aux = Surfaces.listSurface(SurfaceImage('walk_back2.png'), (3,1))
        self.images.update({DIRECTION_UP : aux})

        self.rect = aux[0].get_rect()
        self.last_direction = DIRECTION_DOWN
        self.image = self.images[self.last_direction][self.STAND]

        self.last_move = 1 # last move who took charactor
        self.is_moving = 0 # if is moving
        self.__time = 0 # to make transition of images when is moving
        self.__has_change = 0 # to change images when is moving in a time
        self.__delay = MTS * 2./3 # delay to change a certain frame
        
    def move(self, direction):
        '''when a charactor starts to move'''
        self.is_moving = 1
        self.dirty = 1
        self.__time = time.time()
        if direction == self.last_direction:
            if self.last_move == 2:
                self.image = self.images[self.last_direction][0]
                self.last_move = 0
            else:
                self.image = self.images[self.last_direction][2]
                self.last_move = 2
        else:
            self.image = self.images[direction][0]
            self.last_direction = direction
            self.last_move = 0

    def stand(self):
        '''when charactor was placed or is standing in a sector
        standing in a sector occurs when charactor finished a move'''
        self.dirty = 1
        self.image = self.images[self.last_direction][self.STAND]
        self.is_moving = 0
        self.__has_change = 0

    def facingTo(self, direction):
        '''change the facing view if charactor can't move'''
        if direction != self.last_direction:
            self.dirty = 1
            self.last_direction = direction
            self.image = self.images[self.last_direction][self.STAND]

    def notify(self, event):
        '''notifies this object about what method must has has execute'''
        # if not moving and system has asks to move
        if not self.is_moving and isinstance(event, CharactorMoveRequest):
            # if movement is possible
            if self.charactor.sector.movePossible(event.direction):
                self.move(event.direction)
            else:
                self.facingTo(event.direction)
        elif isinstance(event, CharactorPlaceEvent): # put charactor in map
            self.stand()
        elif isinstance(event, CharactorMoveEvent): # charactor has moved
            self.stand()
        elif self.is_moving: # if charactor performs a movement
            if (time.time()-self.__time) > (self.__delay)\
            and self.__has_change == 0: # change images in a certain time while is moving
                self.dirty = 1
                self.__has_change = 1
                self.image = self.images[self.last_direction][self.STAND]

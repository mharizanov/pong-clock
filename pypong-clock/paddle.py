#!/usr/bin/python
""" A paddle for Pong
"""
import pygame
import math
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Paddle(pygame.sprite.DirtySprite):
    """Represents a game paddle"""
    
    def __init__(self, position, surface, playarea):
        #call the parent class init
        """
        :param position: Pygame Rect describing the size and position
        :param surface: surface the paddle is on
        :param playarea: area where game is played
        """
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.Surface([position.width, position.height])
        self.image.fill(WHITE)
        self._rect = self.image.get_rect()
        self._rect.top = position.top
        self._rect.left = position.left
        self.velocity = 0.0
        self.surface = surface
        self.track_to_position = position[1]
        self.play_area = playarea
        self.miss_value = 0
        self.random_hit_range = range(int(self._rect.height / 2 *- 0.85),
                                      int(self._rect.height / 2 * .85) + 1)
        self.deflection_values = self.create_ball_spin_dictionary()
        self.dirty = 1

    def track_to(self, position):
        """ The paddle will move to the position passed"""
        position = int(position)
        #print 'track to position set to: ' + str(position)
        if position < 0:
            self.track_to_position = position + self.miss_value
        else:
            self.track_to_position = position + self.miss_value
        
        #randomize where the ball will hit the paddle
        if self.miss_value == 0:
            variance = random.choice(self.random_hit_range)
            self.track_to_position = position + variance

    def get_deflection_value(self, ball_center):
        """
        Returns a multiplier to be used to modify the vertical velocity of the ball based on where on the paddle the
        hit occurred.
        :param ball_center: int where the hit occurred.
        :rtype : int
        """

        #deflection_values has the lookups
        offset = self._rect.centery - ball_center
        if offset in self.deflection_values:
            return self.deflection_values[offset]
        else:
            return 0

    def create_ball_spin_dictionary(self):
        """
        Creates a dictionary of values used to add vertical velocity if the ball hits the
        paddle at the bottom or top quarter of the paddle.
        :rtype :dict
        """
        length = len(self.random_hit_range)
        quartiles = [self.random_hit_range[i*length // 4: (i+1)*length // 4] for i in range(4)]
        quartiles[1].extend(quartiles[2])
        quartiles.pop(2)
        for q in quartiles:
            print q
        # quartiles start at negative values and increase to positives
        # [-10, -9, -8, -7, -6]
        # [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]
        # [5, 6, 7, 8, 9, 10]
        ball_spin = {}
        multipliers = list(reversed(range(-1, 2)))
        counter = 0
        for quarter in quartiles:
            print 'quarter', quarter, multipliers[counter]
            for off_val in quarter:
                ball_spin[off_val] = multipliers[counter]
            counter += 1
        return ball_spin

    def allow_score(self):
        """Allows the ball to pass the paddle and score"""
        miss_value = .7 * self._rect.height + random.randrange(0, 3 * self._rect.height) * random.choice([-1, 1])
        self.miss_value = miss_value

    def scored(self, side):
        """Delegate called when the ball scores a goal. Resets the miss_value"""
        self.miss_value = 0

    @property
    def rect(self):
        """ Returns a Pygame.Rect object representing the location and size of the paddle"""
        return self._rect

    def update(self, surface, original_background):
        """Overrides DirtySprite's update method"""
        at_boundary = None
        turn_velocity = 0
        #create a new _rect to hit-test against
        t_position = pygame.Rect((self._rect.left, self._rect.top + self.velocity, self._rect.width, self._rect.height))

        #only stop moving if we will move above the top or bottom edge and tracking beneath or above it
        if t_position.top <= self.play_area.top and \
                                self.track_to_position - self._rect.height / 2  < self.play_area.top:
            turn_velocity = self.play_area.top - self._rect.top  # move next to border
            at_boundary = True

        if t_position.bottom >= self.play_area.top + self.play_area.height \
            and self.track_to_position + self._rect.height / 2 > \
                                self.play_area.top + self.play_area.height:
            turn_velocity = self.play_area.top + self.play_area.height - self._rect.bottom
            at_boundary = True

        if at_boundary is True:
            self._rect.move_ip(0, turn_velocity)
            surface.blit(original_background, (0, 0))
            self.dirty = 1            
            return            

        #check if we have arrived at track_to, if not set velocity
        #track so the centery of the paddle is equal to the track to value
        high = self._rect.centery + (math.fabs(self.velocity) + 0)
        low = self._rect.centery - (math.fabs(self.velocity) + 0)
       
        #high and low cover an area around the center       
        if high >= self.track_to_position >= low:
            #print 'in range'
            if self.track_to_position == self._rect.centery:
                if self.velocity != 0.0:
                    self.dirty = 0
                    return
            else:  # in range to hit
                self._rect.move_ip(0, self.track_to_position - self._rect.centery )
                self.dirty = 1
                #draw the short move
                surface.blit(original_background, (0, 0))
                return

        else:
            #out of range, keep on moving
            if t_position.centery < self.track_to_position: 
                #the paddle is above the exit
                self.velocity = 16.0
            else:
                self.velocity = -16.0

        #draw the image on the background
        self._rect.move_ip(0, self.velocity)
        surface.blit(original_background, (0, 0))
        self.dirty = 1


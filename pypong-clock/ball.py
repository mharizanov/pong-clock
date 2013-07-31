#!/usr/bin/python
"""Ball used in pong"""
import pygame
from event import Event
import math
import random

       
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BALL_BORDER = 1    # Width of the border around the ball
MAX_HORIZONTAL_VELOCITY = 6
MAX_VERTICAL_VELOCITY = 4


class Ball(pygame.sprite.DirtySprite):
    """Ball used for Pong"""
    def __init__(self, position, paddles, velocity, surface, playarea):
        #call the parent class init
        """
        :param position: Pygame Rect describing the ball
        :param paddles: Reference to the paddles for collision checking
        :param velocity: Initial velocity of the ball
        :param surface: pygame surface
        :param playarea: area within the surface used for gameplay
        """
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.Surface([position.width, position.height])
        self.image.fill(BLACK)
        white_center = pygame.Rect(
            (BALL_BORDER, BALL_BORDER,  position.width - 2 * BALL_BORDER,
             position.height - 2 * BALL_BORDER))
        self.image.fill(WHITE, white_center)
        self.rect = self.image.get_rect()
        self.rect.top = position.top
        self.rect.left = position.left
        self.dirty = 2  # ball is always moving
        self.paddles = paddles
        self.surface = surface
        self._initial_velocity = list(velocity)
        self.velocity = list(velocity)
        self.point_scored = Event()
        self.left_paddle_intercept = Event()
        self.right_paddle_intercept = Event()
        self.need_updated_intercept_position = True
        self.playarea = pygame.Rect(playarea)
        self.top_bottom_offset = \
            (self.surface.get_height() - self.playarea.height) / 2
        self.left_right_offset = \
            (self.surface.get_width() - self.playarea.width) / 2
        self.force_score_side = "none"
        self.paddle_track_to = [0, 0]

    @property
    def initial_velocity(self):
        return self._initial_velocity

    @initial_velocity.setter
    def initial_velocity(self, value):
        assert isinstance(value, list)
        self._initial_velocity = value

    def force_score(self, side):
        """forces the ball to score a point
        :param side: the side that will be forced to allow a score
        """
        sides = ['left', 'right', 'none']
        if not side in sides:
            raise ValueError("The side passed in, {}, is not valid".format(side))
        self.force_score_side = side

    def update_intercept_location(self):
        """ Converts the velocity and location to an intercept location. """
        self.need_updated_intercept_position = False
        # we convert to int because that's how the ball moves across the screen.
        # This prevents scenarios where the ratio is 3.9/2.0 which causes the
        # angle returned to be inaccurate and results in missed balls
        angle_b = math.degrees(math.atan(math.fabs(int(self.velocity[1])) / 
                                         math.fabs(int(self.velocity[0]))))        
        print self.velocity
        angle_c = 180 - (90 + angle_b)
        left = False

        if self.velocity[0] < 0:  # Heading left (origin is 0)
            distance_c = self.rect.left - self.left_right_offset
            left = True
        else:
            # - self.left_right_offset is already included in the play_area
            distance_c = self.playarea.width + self.left_right_offset - \
                         (self.rect.left + self.rect.width)
            #distance_c = self.play_area.width - self._rect.left
       
        print 'distance c', distance_c
        
        down = False    
        if self.velocity[1] > 0: 
            down = True

        height = (distance_c * math.sin(math.radians(angle_b))) / math.sin(math.radians(angle_c)) 
        #height += self._rect[3] / 2

        if down is True:
            height = self.rect.centery + height
        else:
            height = self.rect.centery - height

        # Here we check to see if self.force_score = none. If it is 'left'
        # or 'right' we fudge the intercept position to hopefully miss.
        
        if left is True:
            #if self.force_score_side == "left": height += miss_value
            self.left_paddle_intercept(height)
            self.paddle_track_to[0] = height
            #print 'projected left exit location ' + str(height)
        else:
            #if self.force_score_side == "right": height += miss_value
            self.right_paddle_intercept(height)
            self.paddle_track_to[1] = height
            #print 'projected right exit location ' + str(height)

    def update(self, surface, original_background):
        """
        update is provided for DirtySprite
        :param surface:
        :param original_background:
        :return:
        """
        t_position = pygame.Rect((self.rect.left + self.velocity[0],
                                  self.rect.top + self.velocity[1],
                                  self.rect.width, self.rect.height))
        # Check collision with paddles       
        for paddle in self.paddles:
            if t_position.colliderect(paddle.rect) == 1:      # Collision occurred
                print 'collision - velocity in = ', self.velocity
                paddle_deflection = paddle.get_deflection_value(self.rect.centery)
                assert isinstance(paddle_deflection, int)
                if math.fabs(self.velocity[1] + paddle_deflection) \
                        < MAX_VERTICAL_VELOCITY:
                    self.velocity[1] += paddle_deflection
                if math.fabs(self.velocity[0] * -1.05) < MAX_HORIZONTAL_VELOCITY:
                    self.velocity[0] *= -1.05
                else:
                    self.velocity[0] *= -1

                self.need_updated_intercept_position = True
                # Move and return
                self.rect.move_ip(self.velocity)
                self.surface.blit(original_background, (0, 0))
                return
        
        # check for top and bottom bounce
        if t_position.top < 0 + self.top_bottom_offset:	    
            self.velocity[1] *= -1.0
            self.need_updated_intercept_position = True
        # bottom edge bounce
        elif t_position.bottom > self.surface.get_height() - self.top_bottom_offset:
            self.velocity[1] *= -1.0
            self.need_updated_intercept_position = True
        
        #Check to see if we score
        elif t_position.right > self.surface.get_width():   # score
            #increase score for left player
            self.rect.top = (self.surface.get_height()/2)
            self.rect.left = (self.surface.get_width()/2)
            #set the new velocity to a random between initial and max
            self.velocity[0] = random.randint(self._initial_velocity[0], MAX_HORIZONTAL_VELOCITY)
            self.velocity[1] = random.randint(self._initial_velocity[1], MAX_VERTICAL_VELOCITY)
            self.velocity[0] *= -1.0  # change direction
            self.need_updated_intercept_position = True
            self.point_scored('left')
            self.force_score_side = 'none'
            #print 'balls track to ', self.paddle_track_to, self.rect.centery
            #return
        elif t_position.left < 0:
            #new ball
            self.rect.top = (self.surface.get_height()/2)
            self.rect.left = (self.surface.get_width()/2)   
            #set the new velocity to a random between initial and max
            self.velocity[0] = random.randint(self._initial_velocity[0], MAX_HORIZONTAL_VELOCITY)
            self.velocity[1] = random.randint(self._initial_velocity[1], MAX_VERTICAL_VELOCITY)
            #self.velocity[0] *=	-1  #change direction
            #print 'right player score - ball exited at: ' + str(t_position.top)
            self.point_scored('right')
            self.force_score_side = 'none'
            self.need_updated_intercept_position = True
            #print 'balls track to ', self.paddle_track_to, self.rect.centery
            #return
        
        #move using the new velocity
        self.rect.move_ip(self.velocity)
        self.surface.blit(original_background, (0, 0))

        if self.need_updated_intercept_position is True:
            self.update_intercept_location()

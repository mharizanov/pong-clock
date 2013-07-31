#!/usr/bin/python

# Copyright 2013 Don Clark - donclark@gmail.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import pygame
import datetime
from ball import Ball
from paddle import Paddle
from scoredisplay import ScoreDisplay
import os

original_background = None
background = None

#Set the framebuffer device to be the TFT
os.environ["SDL_FBDEV"] = "/dev/fb1"

#RESOLUTION = (960, 468)
RESOLUTION = (128, 160)     # This is the resolution of the 1.8" TFT screen
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_HEIGHT = 15
PADDLE_WIDTH = 3
BALL_WIDTH = 7
BALL_HEIGHT = 7
PADDLE_GUTTER_OFFSET = 4  	# Offset for the paddles
CENTER_DIVIDER_SIZE = 2		# Size of the squares that divide the playing area in half
FIELD_EDGE_WIDTH = 3		# Edging on the top and bottom playing area
FIELD_EDGE_HEIGHT = 1		# Height of edging
FIELD_EDGE_OFFSET = 2		# Offset between the display surface edge and the edging
CAN_RESET_HOUR = True	    # On the hour we reset the score to 00, 00

def main():

    pygame.init()
    #RESOLUTION = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    pygame.mouse.set_visible(False)  # Closes #4
    SCREEN = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
    #SCREEN = pygame.display.set_mode(RESOLUTION)

    # Calculate the play area
    play_area = pygame.Rect(PADDLE_GUTTER_OFFSET + PADDLE_WIDTH, FIELD_EDGE_OFFSET + FIELD_EDGE_HEIGHT, SCREEN.get_width() -
                           (2 * (PADDLE_GUTTER_OFFSET + PADDLE_WIDTH)), SCREEN.get_height() - (2 *(FIELD_EDGE_OFFSET + FIELD_EDGE_HEIGHT)))

    left_paddle = Paddle(pygame.Rect((PADDLE_GUTTER_OFFSET, RESOLUTION[1]/2 -
                                      (PADDLE_HEIGHT/2), PADDLE_WIDTH, PADDLE_HEIGHT)), SCREEN, play_area)
    right_paddle = Paddle(pygame.Rect((RESOLUTION[0] -
                                       (PADDLE_WIDTH + PADDLE_GUTTER_OFFSET), RESOLUTION[1]/2 -
                                       (PADDLE_HEIGHT/2), PADDLE_WIDTH, PADDLE_HEIGHT )), SCREEN, play_area)

    # Configure the game ball
    ball_pos = pygame.Rect((SCREEN.get_width()/2), (SCREEN.get_height()/2), BALL_WIDTH, BALL_HEIGHT)
    ball_paddles = [left_paddle, right_paddle]
    game_ball = Ball(ball_pos, ball_paddles, (2.0, 3.0), SCREEN, play_area)

    # Configure the score display which will show the time
    right_score_display = ScoreDisplay((RESOLUTION[0] / 2 + 18, 20, 30, 50), (15, 28), 00, 'right')
    left_score_display = ScoreDisplay((RESOLUTION[0] / 2 - 18, 20, 60, 100), (15, 28), 00, 'left', True)

    # Wire up the events we will be using
    game_ball.point_scored += right_score_display.increment_score
    game_ball.point_scored += left_score_display.increment_score
    game_ball.point_scored += left_paddle.scored
    game_ball.point_scored += right_paddle.scored
    game_ball.right_paddle_intercept += right_paddle.track_to
    game_ball.left_paddle_intercept += left_paddle.track_to

    # Calculations for the center divider
    # build a range with the y pos for the center dots
    CENTER_DIVIDER_Y = CENTER_DIVIDER_SIZE
    if SCREEN.get_height() / CENTER_DIVIDER_SIZE % 2 == 0:
        CENTER_DIVIDER_Y = CENTER_DIVIDER_SIZE / 2

    CENTER_DIVIDER_Y = range(CENTER_DIVIDER_Y, SCREEN.get_height(),
                             2 * CENTER_DIVIDER_SIZE)

    CENTER_DIVIDER_X = (SCREEN.get_width() / 2) - (CENTER_DIVIDER_SIZE / 2)

    # Calculations for the top and bottom dividers
    FIELD_EDGE_X = FIELD_EDGE_WIDTH
    if SCREEN.get_width() % 2 == 0:
        FIELD_EDGE_X = FIELD_EDGE_WIDTH / 2
    field_edge_x = range(FIELD_EDGE_X, SCREEN.get_width(), 2 * FIELD_EDGE_WIDTH)

    Clock = pygame.time.Clock()

    #background = pygame.Surface(RESOLUTION, -2147483648)
    #background = pygame.display.set_mode(RESOLUTION)
    background = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
    background.fill(BLACK)

    # Draw the background - top and bottom edges and the center divider
    for x in field_edge_x:
        field_edge_line_top = pygame.Rect(x, FIELD_EDGE_OFFSET, FIELD_EDGE_WIDTH, FIELD_EDGE_HEIGHT)
        background.fill(WHITE, field_edge_line_top)
        bottom_y = SCREEN.get_height() - (FIELD_EDGE_HEIGHT + FIELD_EDGE_OFFSET)
        field_edge_line_top = pygame.Rect(x, bottom_y, FIELD_EDGE_WIDTH, FIELD_EDGE_HEIGHT)
        background.fill(WHITE, field_edge_line_top)

    for y in CENTER_DIVIDER_Y:
        center_dot = pygame.Rect(CENTER_DIVIDER_X, y, CENTER_DIVIDER_SIZE, CENTER_DIVIDER_SIZE)
        background.fill(WHITE, center_dot)

    SCREEN.blit(background, (0, 0))
    pygame.display.flip()
    original_background = background.copy()

    # Create the DirtySprite group
    # We're using ordered updates so that we can force the score on the lowest Z
    # so that the ball appears on top of the score
    game_group = pygame.sprite.OrderedUpdates()
    for digit in left_score_display.update_group:
        game_group.add(digit)

    for digit in right_score_display.update_group:
        game_group.add(digit)

    game_group.add(left_paddle)
    game_group.add(right_paddle)
    game_group.add(game_ball)

    # Set a filter on the allowed events in pygame
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

    tic = 0
    RUNNING = True

    while RUNNING:
        Clock.tick(60)

        tic += 1
        if tic % 30 == 0:
            tic = 0
            check_time(right_paddle, left_paddle, left_score_display, right_score_display, game_ball)

        # Process the sprites.
        game_group.clear(SCREEN, background)
        game_group.update(SCREEN, original_background)
        dirty_rects = game_group.draw(SCREEN)
        pygame.display.update(dirty_rects)

        # These are here for debugging - if we are full screen we can't quit without these.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
            elif event.type == pygame.KEYDOWN:
                #if pygame.key == pygame.K_ESCAPE:
                    RUNNING = False

    pygame.quit()
    sys.exit            # this is here to play nice with


def check_time(right_paddle, left_paddle, left_score, right_score, ball):
    """ Compares the current time of the computer to the score.
    If different it forces a miss to increase the score"""
    global CAN_RESET_HOUR
    now = datetime.datetime.now()
    hour = now.strftime("%I")

    if left_score.score < int(hour):
        right_paddle.allow_score()
        return
    if right_score.score < now.minute:
        left_paddle.allow_score()
        CAN_RESET_HOUR = True
        return
    else:
        ball.initial_velocity = [3.0, 2.0]
    if CAN_RESET_HOUR is True:
        if now.minute == 0:		# reset on the hour.
            right_score.reset_score()
            left_score.reset_score()
            CAN_RESET_HOUR = False
            return

if __name__ == '__main__':
    main()

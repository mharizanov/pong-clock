#!/usr/bin/env python

import pygame.sprite
########################################################################

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class SegmentedNumber(pygame.sprite.DirtySprite):
    """Creates a segmented number"""

    #----------------------------------------------------------------------
    def __init__(self, position, display_digit='_'):
        """
        Creates a segmented number.
        position - Rect - x,y are the start position, width, height are the size of a single digit
        display_digit - what number(s) to draw on the screen.
        
        """

        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        #Draw number into this surface
        self.image = pygame.Surface([position.width, position.height])
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.top = position.top
        self.rect.left = position.left
        #define values for segments
        self.number_height = position.height 
        self.bar_width = self.number_height / 6
        self.number_width = position.width 
        self.half_number_height = self.number_height / 2
        self.set_number(display_digit)


    #----------------------------------------------------------------------
    def set_number(self, number):
        """draws the number passed in to self.image"""
        NUMBER_NAMES = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five',
                        '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '0': 'zero', '_': 'blank'}
        numbers = list(str(number))

        number_instructions = []
        position = [0, 0]
        for number in numbers:
            mtd = getattr(self, NUMBER_NAMES[number])
            print str(mtd)
            number_instructions = mtd(position)

        #number_instructions has the rects to draw the number into self.image
        self.image = self.original_image.copy()
        for instruction in number_instructions:
            self.image.fill(WHITE, instruction)

        self.dirty = 1

    #----------------------------------------------------------------------
    def update(self, surface, original_background):
        """DirtySprite Updates the displayed number"""

        original_background.blit(self.image, self.rect)
        self.dirty = 1

    def one(self, position=(0, 0)):
        """ Draw a 1 """
        retval = []
        print 'position', position
        retval.append(self.segment_b(position))
        retval.append(self.segment_c(position))
        print retval
        return retval

    def two(self, position):
        """ Draw a 2 """
        retval = []
        retval.append(self.segment_a(position))
        retval.append(self.segment_b(position))
        retval.append(self.segment_g(position))
        retval.append(self.segment_e(position))
        retval.append(self.segment_d(position))
        return retval

    def three(self, position):
        """ Draw a 3 """
        retval = []
        retval.append(self.segment_a(position))
        retval.append(self.segment_b(position))
        retval.append(self.segment_g(position))
        retval.append(self.segment_c(position))
        retval.append(self.segment_d(position))
        return retval

    def four(self, position):
        """ Draw a 4 """
        retval = []
        retval.append(self.segment_f(position))
        retval.append(self.segment_g(position))
        retval.append(self.segment_b(position))
        retval.append(self.segment_c(position))
        return retval

    def five(self, position):
        """ Draw a 5 """
        retval = []
        retval.append(self.segment_a(position))
        retval.append(self.segment_f(position))
        retval.append(self.segment_g(position))
        retval.append(self.segment_c(position))
        retval.append(self.segment_d(position))
        return retval

    def six(self, position):
        """ Draw a 6 """
        retval = []
        retval.append(self.segment_e(position))
        retval.append(self.segment_f(position))
        retval.append(self.segment_g(position))
        retval.append(self.segment_c(position))
        retval.append(self.segment_d(position))
        return retval

    def seven(self, position):
        """ Draw a 7 """
        retval = []
        retval.append(self.segment_a(position))
        retval.append(self.segment_b(position))
        retval.append(self.segment_c(position))
        return retval


    def eight(self, position):
        """ Draw an 8 """
        retval = []
        retval.append(self.segment_a(position))
        retval.append(self.segment_b(position))
        retval.append(self.segment_c(position))
        retval.append(self.segment_d(position))
        retval.append(self.segment_e(position))
        retval.append(self.segment_f(position))
        retval.append(self.segment_g(position))
        return retval


    def nine(self, position):
        """ Draw a 9 """
        retval = []
        retval.append(self.segment_a(position))
        retval.append(self.segment_b(position))
        retval.append(self.segment_c(position))
        retval.append(self.segment_f(position))
        retval.append(self.segment_g(position))
        return retval

    def zero(self, position):
        """ Draw a 0 """
        retval = []
        retval.append(self.segment_a(position))
        retval.append(self.segment_b(position))
        retval.append(self.segment_c(position))
        retval.append(self.segment_d(position))
        retval.append(self.segment_e(position))
        retval.append(self.segment_f(position))
        return retval

    def blank(self, position):
        retval = []
        return retval

    #in the segments position refers to the origin for the number.
    #segment names from http://en.wikipedia.org/wiki/Seven-segment_display
    def segment_a(self, position):
        axis_x = position[0]
        axis_y = position[1]
        return pygame.Rect(axis_x, axis_y, self.number_width, self.bar_width)

    def segment_b(self, position):
        axis_x = position[0] + self.number_width - self.bar_width
        axis_y = position[1]
        return pygame.Rect(axis_x, axis_y, self.bar_width, self.half_number_height)

    def segment_c(self, position):
        axis_x = position[0] + self.number_width - self.bar_width
        axis_y = position[1] + self.half_number_height
        return pygame.Rect(axis_x, axis_y, self.bar_width, self.half_number_height)

    def segment_d(self, position):
        axis_x = position[0]
        axis_y = position[1] + self.number_height - self.bar_width
        return pygame.Rect(axis_x, axis_y, self.number_width, self.bar_width)

    def segment_e(self, position):
        axis_x = position[0]
        axis_y = position[1] + self.half_number_height
        return pygame.Rect(axis_x, axis_y, self.bar_width, self.half_number_height)

    def segment_f(self, position):
        axis_x = position[0]
        axis_y = position[1]
        return pygame.Rect(axis_x, axis_y, self.bar_width, self.half_number_height)

    def segment_g(self, position):
        #x = position[0] + bar_width
        #y = position[1] + half_number_height - (bar_width / 2)
        #return (x, y, number_width - (2 * bar_width), bar_width)        
        axis_x = position[0]
        axis_y = position[1] + self.half_number_height - (self.bar_width / 2)
        return pygame.Rect(axis_x, axis_y, self.number_width, self.bar_width)


            
    

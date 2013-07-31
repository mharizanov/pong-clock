#!/usr/bin/env python
#coding:utf-8
# Author:  Don Clark --<donclark@gmail.com>
# Purpose: Displays a score
# Created: 06/12/13
########################################################################
import pygame.sprite
from event import Event
from segmentednumber import SegmentedNumber



class ScoreDisplay:
    """Displays the score by grouping segmentednumbers together. 
    The value displayed is zero filled."""

    #----------------------------------------------------------------------
    def __init__(self, position, digit_size, score, name, justified = False):
        """Constructor
        position - A pygame _rect object that determines the location of the display.
        digit_size - A tuple with the height and width of the digit to be displayed.
        score - integer showing the initial score
        name - the name of the display e.g. 'left' or 'right'
        justified - Boolean if true the ScoreDisplay is right justified Default = False
        :type self: ScoreDisplay
        """
        self.position = pygame.Rect(position)
        self.digit_size = digit_size
        self.display_numbers = []
        self.update_group = []
        self.score = score
        self.update_score = Event()
        self.justified = justified
        self.display_digits_count = 2    # the number of digits to show
        self.numbers = str(self.score).zfill(self.display_digits_count)
        self.name = name
        
        if justified:
            self.position[0] -= ((self.digit_size[0] * self.display_digits_count)
            + ((self.digit_size[0] / 4) * (self.display_digits_count - 1)))

        self.setup_score_area()
    #----------------------------------------------------------------------
    def setup_score_area(self):
        """Helper function to configure the score area"""
        #create the segmentednumbers and add them to self.display_numbers
        offset = 0
        for number in self.numbers:
            seg_number = SegmentedNumber(pygame.Rect([self.position[0] + offset, self.position[1], self.digit_size[0], self.digit_size[1]]), number)
            self.update_group.append(seg_number)
            print 'segment number ' , offset
            offset = offset + self.digit_size[0] + (self.digit_size[0] / 4)
    
    #----------------------------------------------------------------------
    def increment_score(self, side):
        """updates the score"""
        if side == self.name:
            self.score += 1
            self.update_display()
    
    #----------------------------------------------------------------------
    def update_display(self):
        """updates the display with the current score"""
        
        counter = 0
        current_score = str(self.score).zfill(self.display_digits_count)
        for digit in current_score:
            self.update_group[counter].set_number(digit)
            counter += 1 
         
        
    #----------------------------------------------------------------------
    def reset_score(self):
        """Resets the score to 00"""
        self.score = 0
        self.update_display()
        
            
        
    
    
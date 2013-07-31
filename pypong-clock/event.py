#!/usr/bin/python

""" A lightweight event handler class
Usage: Add Event() as a field to your class in  __init__ 
self.score = Event()

Assign a delegate to the event in your code:
ball.score += delegate
"""


class Event:

    def __init__(self):
        self.handlers = set()  # set ignores duplicates during add

    def add_handler(self, handler):
        """ Adds the handler passed in to the list"""
        #print 'handler = ', handler
        self.handlers.add(handler)
        #print len(self.handlers)
        return self

    def remove_handler(self, handler):
        """ Removes the handler passed in from the list. """
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("This is not an event currently being handled")
        return self

    def __call__(self, *args, **kwargs):
        """ Will call the function added with handle"""
        for handler in self.handlers:
            #print handler
            handler(*args, **kwargs)

    def __len__(self):
        """
        Returns the number of handlers.

        :return: int
        """
        return len(self.handlers)

    def __str__(self):
        """
        String representation of the delegates

        :return: str
        """
        retval = ''
        for handler in self.handlers:
            retval = retval + ' ' + str(handler)
        return retval

    __iadd__ = add_handler	    # += support
    __isub__ = remove_handler   # -= support

'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

#------------------------------------------------------------------------------
class DatabaseCorrupted(UserWarning):
    '''
    The database content is inconsistent.
    '''
    def __init__(self, message):
        self.message = message



#------------------------------------------------------------------------------
class WrongApiVersion(UserWarning):
    '''
    The API version does not match.
    '''
    def __init__(self, message):
        self.message = message
        
'''
This file is part of ICE Security Management

Created on 24 janv. 2010

@author: diabeteman
'''

#______________________________________________________________________________
class WrongApiVersion(UserWarning):
    '''
    The API version does not match.
    '''
    def __init__(self, message):
        self.message = message
        
#______________________________________________________________________________
class MalformedXmlResponse(UserWarning):
    '''
    Unexpected format when reading an API xml response.
    '''
    def __init__(self, message):
        self.message = message

#______________________________________________________________________________
class DatabaseCorrupted(UserWarning):
    '''
    The database contents are inconsistent.
    '''
    def __init__(self, message):
        self.message = message

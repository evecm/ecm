'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

#------------------------------------------------------------------------------
class WrongApiVersion(UserWarning):
    '''
    The API version does not match.
    '''
    def __init__(self, message):
        self.message = message
        
#------------------------------------------------------------------------------
class MalformedXmlResponse(UserWarning):
    '''
    Unexpected format when reading an API xml response.
    '''
    def __init__(self, message):
        self.message = message

#------------------------------------------------------------------------------
class DatabaseCorrupted(UserWarning):
    '''
    The database content is inconsistent.
    '''
    def __init__(self, message):
        self.message = message

'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''

import time

def print_time(time_in_seconds):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time_in_seconds))

def print_date(time_in_seconds):
    return time.strftime("%Y-%m-%d", time.gmtime(time_in_seconds))

def limit_text_size(text, max_size):
    if len(text) < max_size:
        return text
    else:
        return text[:(max_size - 3)] + "..."
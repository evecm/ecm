'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''

def print_time(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def print_time_min(date):
    return date.strftime("%Y %b %d - %H:%M")

def print_date(date):
    return date.strftime("%Y-%m-%d")

def limit_text_size(text, max_size):
    if len(text) < max_size:
        return text
    else:
        return text[:(max_size - 3)] + "..."
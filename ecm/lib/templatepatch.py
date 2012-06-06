'''
Created on Jun 6, 2012

@author: diabeteman
'''
import re
from django.template import base

# monkey patch django: allow template tags to span over multiple lines
base.tag_re = re.compile('(%s.*?%s|%s.*?%s|%s.*?%s)' % (re.escape(base.BLOCK_TAG_START), 
                                                        re.escape(base.BLOCK_TAG_END),
                                                        re.escape(base.VARIABLE_TAG_START), 
                                                        re.escape(base.VARIABLE_TAG_END),
                                                        re.escape(base.COMMENT_TAG_START), 
                                                        re.escape(base.COMMENT_TAG_END)),
                         re.DOTALL)

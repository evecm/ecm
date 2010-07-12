'''
This file is part of ICE Security Management

Created on 7 juil. 2010
@author: diabeteman
'''
from ism import settings
from ism.core import db

from PIL import ImageFont, ImageDraw, Image
import os.path, unicodedata, re

FONT_FILE = os.path.join(settings.MEDIA_ROOT, "fonts/VERDANAB.TTF")
IMG_DIR = os.path.join(settings.MEDIA_ROOT, "img/gen")
ILLEGAL_RE = re.compile(r"['\s\":/\\;,\?!\*\^#&\(\)\[\]\{\}]")
TRANSPARENT = (0,0,0,0)
WHITE = (255,255,255,255)

def generateImage(text, width=30):
    font = ImageFont.truetype(FONT_FILE, 15)
    
    length = len(text)*10 + 10
    
    image = Image.new("RGBA", (length, width), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.text((5,5), text, font=font, fill=WHITE)
    image = image.rotate(90)
    
    filename = unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
    filename = ILLEGAL_RE.subn("_", filename)[0] + ".png"
        
    image.save(os.path.join(IMG_DIR, filename), "PNG")
    
    return settings.MEDIA_URL + "img/gen/" + filename

def getImage(text):
    filename = unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
    filename = ILLEGAL_RE.subn("_", filename)[0] + ".png"
    
    if os.path.exists(os.path.join(IMG_DIR, filename)):
        return settings.MEDIA_URL + "img/gen/" + filename
    else:
        return generateImage(text)

        
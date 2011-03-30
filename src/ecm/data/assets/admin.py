"""
The MIT License - EVE Corporation Management

Copyright (c) 2010 Robin Jarry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__date__ = "2010-05-14"
__author__ = "diabeteman"


from django.contrib import admin
from ecm.data.assets.models import DbAsset, DbAssetDiff

class DbAssetAdmin(admin.ModelAdmin):
    list_display = ['itemID', 'locationID', 'hangarID', 'container1', 'container2', 
                    'typeID', 'quantity', 'flag', 'singleton', 'hasContents']

class DbAssetDiffAdmin(admin.ModelAdmin):
    list_display = ['locationID', 'hangarID', 'typeID', 'quantity', 'date', 'new']
    


admin.site.register(DbAsset, DbAssetAdmin)
admin.site.register(DbAssetDiff, DbAssetDiffAdmin)

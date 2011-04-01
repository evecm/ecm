# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


__date__ = "2010-06-03"
__author__ = "diabeteman"


from ecm.data.accounting.models import JournalEntry, EntryType
from django.contrib import admin

#------------------------------------------------------------------------------

class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'date', 'type', 'ownerName1', 'ownerName2', 'amount', 'balance', 'reason']
    search_fields = ['ownerName1', 'ownerName2', 'date']
    list_filter = ['wallet', 'type']

class EntryTypeAdmin(admin.ModelAdmin):
    list_display = ['refTypeID', 'refTypeName']
    search_fields = ['refTypeName']

admin.site.register(JournalEntry, JournalEntryAdmin)
admin.site.register(EntryType, EntryTypeAdmin)
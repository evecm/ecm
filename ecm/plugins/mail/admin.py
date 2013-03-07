# Copyright (c) 2010-2011 Jerome Vacher
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2013 02 22"
__author__ = "Ajurna"

from django.contrib import admin

from ecm.plugins.mail.models import Mail, Recipient, MailingList, Notification

#------------------------------------------------------------------------------
class MailAdmin(admin.ModelAdmin):
    pass

#------------------------------------------------------------------------------
class RecipientAdmin(admin.ModelAdmin):
    pass

#------------------------------------------------------------------------------
class MailingListAdmin(admin.ModelAdmin):
    pass

#------------------------------------------------------------------------------
class NotificationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Mail, MailAdmin)
admin.site.register(Recipient, RecipientAdmin)
admin.site.register(MailingList, MailingListAdmin)
admin.site.register(Notification, NotificationAdmin)
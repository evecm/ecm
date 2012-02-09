# Copyright (c) 2010-2012 Robin Jarry
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

__date__ = '2010-05-17'
__author__ = 'diabeteman'

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
import re
import random
import datetime

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from django.db import models, transaction
from django.conf import settings
from django.utils.hashcompat import sha_constructor
from django.core.validators import RegexValidator

#------------------------------------------------------------------------------
class Setting(models.Model):
    """
    ECM settings stored in the database.
    """
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200, primary_key=True)
    value = models.CharField(max_length=1000, default='')

    def getValue(self):
        return eval(self.value)

    def clean(self):
        eval(self.value)

    def __eq__(self, other):
        return isinstance(other, Setting) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __unicode__(self):
        return u'%s = %s' % (self.name, self.value)
    
    @staticmethod
    def get(name):
        return Setting.objects.get(name=name).getValue()

#------------------------------------------------------------------------------
class UserAPIKey(models.Model):
    """
    API credentials used to associate characters to users
    """
    user = models.ForeignKey(User, related_name='eve_accounts')
    keyID = models.IntegerField(primary_key=True)
    vCode = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=True)

    class Meta:
        ordering = ['user']

    def is_valid_html(self):
        if self.is_valid:
            return '<span class="bold ok">API key valid</span>'
        else:
            return '<span class="bold error">API key invalid</span>'

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return self.keyID * 10000 + self.user_id

    def __unicode__(self):
        try:
            return u"%s owns %d" % (self.user.username, self.keyID)
        except:
            return u"%d owns %d" % (self.user_id, self.keyID)

#------------------------------------------------------------------------------
class ExternalApplication(models.Model):
    """
    Represents external applications to be used along with ECM such as
    bulletin boards or killboards.
    """
    name = models.CharField(max_length=64,
                            unique=True,
                            validators=[RegexValidator(r'^\w+$',
                                                       message='Only letters and digits')])
    url = models.CharField(max_length=1024)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, ExternalApplication) and self.name == other.name

    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class UserBinding(models.Model):
    """
    Allows to bind ECM users to external applications.

    The goal is to enable automatic synchronization of the external
    application's user accesses with ECM user accesses.
    """
    user = models.ForeignKey(User, related_name='bindings')
    external_app = models.ForeignKey(ExternalApplication, related_name='user_bindings')
    external_id = models.IntegerField()
    external_name = models.CharField(max_length=255)

    # override from models.Model
    def clean(self):
        query = UserBinding.objects.filter(external_app=self.external_app)
        if query.filter(user=self.user).exists():
            raise ValidationError('This user already has a binding for the '
                                  'external application "%s"' % self.external_app.name)
        elif query.filter(external_id=self.external_id).exists():
            raise ValidationError('This external_id is already binded for the '
                                  'external application "%s"' % self.external_app.name)
        elif query.filter(external_name=self.external_name).exists():
            raise ValidationError('This external_name is already binded for the '
                                  'external application "%s"' % self.external_app.name)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, UserBinding) and self.id == other.id

    def __unicode__(self):
        return unicode(self.external_name)

#------------------------------------------------------------------------------
class GroupBinding(models.Model):
    """
    Allows to bind ECM groups to external applications.

    The goal is to enable automatic synchronization of the external
    application's user accesses with ECM user accesses.
    """
    group = models.ForeignKey(Group, related_name='bindings')
    external_app = models.ForeignKey(ExternalApplication, related_name='group_bindings')
    external_id = models.IntegerField()
    external_name = models.CharField(max_length=256)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, GroupBinding) and self.id == other.id

    def __unicode__(self):
        return unicode(self.external_name)

#------------------------------------------------------------------------------
class UpdateDate(models.Model):
    """
    Represents the update time of a model's table in the database.
    """
    model_name = models.CharField(primary_key=True, max_length=64)
    update_date = models.DateTimeField()
    prev_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-update_date']

    def __unicode__(self):
        return u"%s updated %s" % (self.model_name, self.update_date)

#------------------------------------------------------------------------------
class ColorThreshold(models.Model):
    """
    Thresholds for security access level coloration.
    """
    color = models.CharField(max_length=64)
    threshold = models.BigIntegerField()

    @staticmethod
    def as_json():
        th = ColorThreshold.objects.values("threshold", "color").order_by("threshold")
        return json.dumps(list(th))

    def __unicode__(self):
        return u"%s -> %d" % (self.color, self.threshold)


#------------------------------------------------------------------------------
class UrlPermission(models.Model):
    """
    Utility class for authorization management in ECM.
    """
    pattern = models.CharField(max_length=256)
    groups = models.ManyToManyField(Group, related_name='allowed_urls')

    def groups_admin_display(self):
        return ', '.join(self.groups.values_list('name', flat=True))
    groups_admin_display.short_description = 'Groups'

    def __unicode__(self):
        return unicode(self.pattern)

    def __eq__(self, other):
        return self.pattern == other.pattern

    def __hash__(self):
        return hash(self.pattern)

def user_has_access(user, target_url):
    """
    Checks if a User has access to the specified target_url.
    """
    for url in UrlPermission.objects.all():
        url_re = re.compile(url.pattern)
        if url_re.match(target_url):
            if set(url.groups.all()).intersection(set(user.groups.all())):
                return True
            else:
                return False
    return False




#------------------------------------------------------------------------------

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                raise ValueError("Activation key not found")
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
            else:
                raise UserWarning("Activation key has expired")
        else:
            raise ValueError("Invalid activation key")

    def create_inactive_user(self, username, email, password):
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        profile = self.create_profile(new_user)

        return new_user, profile
    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def create_profile(self, user):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = sha_constructor(salt+username).hexdigest()
        return self.create(user=user, activation_key=activation_key)


class RegistrationProfile(models.Model):

    ACTIVATED = u"ALREADY_ACTIVATED"

    user = models.OneToOneField(User)
    activation_key = models.CharField('activation key', max_length=40)

    objects = RegistrationManager()

    class Meta:
        verbose_name = 'registration profile'
        verbose_name_plural = 'registration profiles'

    def __unicode__(self):
        return u"Registration information for %s" % self.user

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return self.user_id

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True


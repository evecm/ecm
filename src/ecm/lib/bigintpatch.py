"""module mydjangolib.bigint_patch

A fix for the rather well-known ticket #399 in the django project.

Create and link to auto-incrementing primary keys of type bigint without
having to reload the model instance after saving it to get the ID set in
the instance.
"""

from django.core import exceptions
from django.db.models import fields
from django.db import DatabaseError
from django.utils.translation import ugettext as _

__version__ = "1.0"
__author__ = "Florian Leitner"

class BigIntegerField(fields.IntegerField):
    
    def db_type(self, connection):
        engine = connection.settings_dict.get('ENGINE')
        if 'mysql' in engine:
            return "bigint"
        elif 'oracle' in engine:
            return "NUMBER(19)"
        elif 'postgres' in engine:
            return "bigint"
        elif 'sqlite' in engine:
            return "bigint"
        else:
            raise DatabaseError("DB engine '%s' is not handled" % str(engine))
    
    def get_internal_type(self):
        return "BigIntegerField"
    
    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class BigAutoField(fields.AutoField):
        
    def db_type(self, connection):
        engine = connection.settings_dict.get('ENGINE')
        if 'mysql' in engine:
            return "bigint AUTO_INCREMENT"
        elif 'oracle' in engine:
            return "NUMBER(19)"
        elif 'postgres' in engine:
            return "bigserial"
        elif 'sqlite' in engine:
            return "bigint"
        else:
            raise DatabaseError("DB engine '%s' is not handled" % str(engine))
    
    def get_internal_type(self):
        return "BigAutoField"
    
    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class BigForeignKey(fields.related.ForeignKey):
    
    def db_type(self, connection):
        rel_field = self.rel.get_related_field()
        # next lines are the "bad tooth" in the original code:
        if (isinstance(rel_field, BigAutoField) or
                (not connection.features.related_fields_match_type and
                isinstance(rel_field, BigIntegerField))):
            # because it continues here in the django code:
            # return IntegerField().db_type()
            # thereby fixing any AutoField as IntegerField
            return BigIntegerField().db_type(connection)
        return rel_field.db_type()

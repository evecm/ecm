from django.db.backends import util, BaseDatabaseOperations
from django.db.backends.sqlite3.base import DatabaseOperations
from django.db.models import fields
from django.utils.translation import ugettext as _
from django.db.models.fields.related import ForeignKey
from django.db.backends.postgresql.creation import DatabaseCreation as PostgresDBCreation
from django.db.backends.sqlite3.creation import DatabaseCreation as SQLiteDBCreation
from django.db.backends.oracle.creation import DatabaseCreation as OracleDBCreation
from django.db.backends.mysql.creation import DatabaseCreation as MySQLDBCreation



__version__ = "1.0"
__author__ = "Florian Leitner"

class BigAutoField(fields.AutoField):
    
    description = _("Big (8 byte) integer") 
    
    def get_internal_type(self):
        return "BigAutoField"



PostgresDBCreation.data_types['BigAutoField'] = 'bigserial'
SQLiteDBCreation.data_types['BigAutoField'] = 'bigint'
OracleDBCreation.data_types['BigAutoField'] = 'NUMBER(19)'
MySQLDBCreation.data_types['BigAutoField'] = 'bigint AUTO_INCREMENT'


def db_type_foreignkey(self, connection):
    # The database column type of a ForeignKey is the column type
    # of the field to which it points. An exception is if the ForeignKey
    # points to an AutoField/BigAutoField/PositiveIntegerField/ 
    # PositiveSmallIntegerField, 
    # in which case the column type is simply that of an IntegerField 
    # (or BigIntegerField in the case of BigAutoField). 
    # If the database needs similar types for key fields however, the only
    # thing we can do is making AutoField an IntegerField.
    rel_field = self.rel.get_related_field()
    if isinstance(rel_field, BigAutoField): 
        return fields.BigIntegerField().db_type(connection=connection) 
    if (isinstance(rel_field, fields.AutoField) or
            (not connection.features.related_fields_match_type and
            isinstance(rel_field, (fields.PositiveIntegerField,
                                   fields.PositiveSmallIntegerField)))):
        return fields.IntegerField().db_type(connection=connection)
    return rel_field.db_type(connection=connection)

ForeignKey.db_type = db_type_foreignkey


def convert_values_sqlite(self, value, field):
    """SQLite returns floats when it should be returning decimals,
    and gets dates and datetimes wrong.
    For consistency with other backends, coerce when required.
    """
    internal_type = field.get_internal_type()
    if internal_type == 'DecimalField':
        return util.typecast_decimal(field.format_number(value))
    elif internal_type and internal_type.endswith('IntegerField') or internal_type.endswith('AutoField'): 
        return int(value)
    elif internal_type == 'DateField':
        return util.typecast_date(value)
    elif internal_type == 'DateTimeField':
        return util.typecast_timestamp(value)
    elif internal_type == 'TimeField':
        return util.typecast_time(value)

    # No field, or the field isn't known to be a decimal or integer
    return value

DatabaseOperations.convert_values = convert_values_sqlite



def convert_values_base(self, value, field):
    """Coerce the value returned by the database backend into a consistent type that
    is compatible with the field type.
    """
    internal_type = field.get_internal_type()
    if internal_type == 'DecimalField':
        return value
    elif internal_type and internal_type.endswith('IntegerField') or internal_type.endswith('AutoField'): 
        return int(value)
    elif internal_type in ('DateField', 'DateTimeField', 'TimeField'):
        return value
    # No field, or the field isn't known to be a decimal or integer
    # Default to a float
    return float(value)

BaseDatabaseOperations.convert_values = convert_values_base





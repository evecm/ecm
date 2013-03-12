from django.db.backends import util, BaseDatabaseOperations
from django.db.backends.sqlite3.base import DatabaseOperations
from django.db.models import fields
from django.db.models.fields.related import ForeignKey
from south.modelsinspector import add_introspection_rules
try:
    from django.db.backends.postgresql_psycopg2.creation import DatabaseCreation as PostgresDBCreation
except:
    # fix for django 1.4
    pass
from django.db.backends.sqlite3.creation import DatabaseCreation as SQLiteDBCreation
from django.db.backends.oracle.creation import DatabaseCreation as OracleDBCreation
from django.db.backends.mysql.creation import DatabaseCreation as MySQLDBCreation
from django.utils.datastructures import DictWrapper
from django.db.backends.creation import BaseDatabaseCreation




__version__ = "1.0"
__author__ = "Florian Leitner"

class BigAutoField(fields.AutoField):
    
    description = "Big (8 byte) integer" 
    
    def get_internal_type(self):
        return "BigAutoField"
    
add_introspection_rules([], [r'^ecm\.lib\.bigintpatch\.BigAutoField'])

try:
    PostgresDBCreation.data_types['BigAutoField'] = 'bigserial'
except:
    # fix for django 1.4
    pass
OracleDBCreation.data_types['BigAutoField'] = 'NUMBER(19)'
MySQLDBCreation.data_types['BigAutoField'] = 'bigint AUTO_INCREMENT'
SQLiteDBCreation.data_types['BigAutoField'] = 'integer'
SQLiteDBCreation.data_types_suffix = {
    'AutoField': 'AUTOINCREMENT', 
    'BigAutoField': 'AUTOINCREMENT', 
}



def db_type_suffix(self, connection): 
    data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_") 
    try: 
        return connection.creation.data_types_suffix[self.get_internal_type()] % data 
    except (KeyError, AttributeError): 
        return False 
fields.Field.db_type_suffix = db_type_suffix


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


def sql_create_model(self, model, style, known_models=set()):
    """
    Returns the SQL required to create a single model, as a tuple of:
        (list_of_sql, pending_references_dict)
    """
    opts = model._meta
    if not opts.managed or opts.proxy:
        return [], {}
    final_output = []
    table_output = []
    pending_references = {}
    qn = self.connection.ops.quote_name
    for f in opts.local_fields:
        col_type = f.db_type(connection=self.connection)
        col_type_suffix = f.db_type_suffix(connection=self.connection) 
        tablespace = f.db_tablespace or opts.db_tablespace
        if col_type is None:
            # Skip ManyToManyFields, because they're not represented as
            # database columns in this table.
            continue
        # Make the definition (e.g. 'foo VARCHAR(30)') for this field.
        field_output = [style.SQL_FIELD(qn(f.column)),
            style.SQL_COLTYPE(col_type)]
        if not f.null:
            field_output.append(style.SQL_KEYWORD('NOT NULL'))
        if f.primary_key:
            field_output.append(style.SQL_KEYWORD('PRIMARY KEY'))
        elif f.unique:
            field_output.append(style.SQL_KEYWORD('UNIQUE'))
        if tablespace and f.unique:
            # We must specify the index tablespace inline, because we
            # won't be generating a CREATE INDEX statement for this field.
            field_output.append(self.connection.ops.tablespace_sql(tablespace, inline=True))
        if f.rel:
            ref_output, pending = self.sql_for_inline_foreign_key_references(f, known_models, style)
            if pending:
                pending_references.setdefault(f.rel.to, []).append((model, f))
            else:
                field_output.extend(ref_output)
        if col_type_suffix:
            field_output.append(style.SQL_KEYWORD(col_type_suffix))
        table_output.append(' '.join(field_output))
    for field_constraints in opts.unique_together:
        table_output.append(style.SQL_KEYWORD('UNIQUE') + ' (%s)' % \
            ", ".join([style.SQL_FIELD(qn(opts.get_field(f).column)) for f in field_constraints]))

    full_statement = [style.SQL_KEYWORD('CREATE TABLE') + ' ' + style.SQL_TABLE(qn(opts.db_table)) + ' (']
    for i, line in enumerate(table_output): # Combine and add commas.
        full_statement.append('    %s%s' % (line, i < len(table_output)-1 and ',' or ''))
    full_statement.append(')')
    if opts.db_tablespace:
        full_statement.append(self.connection.ops.tablespace_sql(opts.db_tablespace))
    full_statement.append(';')
    final_output.append('\n'.join(full_statement))

    if opts.has_auto_field:
        # Add any extra SQL needed to support auto-incrementing primary keys.
        auto_column = opts.auto_field.db_column or opts.auto_field.name
        autoinc_sql = self.connection.ops.autoinc_sql(opts.db_table, auto_column)
        if autoinc_sql:
            for stmt in autoinc_sql:
                final_output.append(stmt)

    return final_output, pending_references
BaseDatabaseCreation.sql_create_model = sql_create_model

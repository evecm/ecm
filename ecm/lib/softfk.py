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

__date__ = '2012 6 6'
__author__ = 'diabeteman'

from django.db.models.deletion import DO_NOTHING
from django.db.models.fields.related import ForeignKey, ManyToOneRel
from django.core.management.color import no_style
from south.db.generic import DatabaseOperations, invalidate_table_constraints, flatten

class SoftForeignKey(ForeignKey):
    """
    This field behaves like a normal django ForeignKey only without hard database constraints.
    """
    
    def __init__(self, to, to_field=None, rel_class=ManyToOneRel, **kwargs):
        ForeignKey.__init__(self, to, to_field=to_field, rel_class=rel_class, **kwargs)
        self.on_delete = DO_NOTHING
    
    no_db_constraints = True

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], [r'^ecm\.lib\.softfk\.SoftForeignKey'])

def column_sql(self, table_name, field_name, field, tablespace='', with_name=True, field_prepared=False):
    """
    Creates the SQL snippet for a column. Used by add_column and add_table.
    """

    # If the field hasn't already been told its attribute name, do so.
    if not field_prepared:
        field.set_attributes_from_name(field_name)

    # hook for the field to do any resolution prior to it's attributes being queried
    if hasattr(field, 'south_init'):
        field.south_init()

    # Possible hook to fiddle with the fields (e.g. defaults & TEXT on MySQL)
    field = self._field_sanity(field)

    try:
        sql = field.db_type(connection=self._get_connection())
    except TypeError:
        sql = field.db_type()
    
    if sql:
        
        # Some callers, like the sqlite stuff, just want the extended type.
        if with_name:
            field_output = [self.quote_name(field.column), sql]
        else:
            field_output = [sql]
        
        field_output.append('%sNULL' % (not field.null and 'NOT ' or ''))
        if field.primary_key:
            field_output.append('PRIMARY KEY')
        elif field.unique:
            # Just use UNIQUE (no indexes any more, we have delete_unique)
            field_output.append('UNIQUE')

        tablespace = field.db_tablespace or tablespace
        if tablespace and getattr(self._get_connection().features, "supports_tablespaces", False) and field.unique:
            # We must specify the index tablespace inline, because we
            # won't be generating a CREATE INDEX statement for this field.
            field_output.append(self._get_connection().ops.tablespace_sql(tablespace, inline=True))
        
        sql = ' '.join(field_output)
        sqlparams = ()
        # if the field is "NOT NULL" and a default value is provided, create the column with it
        # this allows the addition of a NOT NULL field to a table with existing rows
        if not getattr(field, '_suppress_default', False):
            if field.has_default():
                default = field.get_default()
                # If the default is actually None, don't add a default term
                if default is not None:
                    # If the default is a callable, then call it!
                    if callable(default):
                        default = default()
                        
                    default = field.get_db_prep_save(default, connection=self._get_connection())
                    default = self._default_value_workaround(default)
                    # Now do some very cheap quoting. TODO: Redesign return values to avoid this.
                    if isinstance(default, basestring):
                        default = "'%s'" % default.replace("'", "''")
                    # Escape any % signs in the output (bug #317)
                    if isinstance(default, basestring):
                        default = default.replace("%", "%%")
                    # Add it in
                    sql += " DEFAULT %s"
                    sqlparams = (default)
            elif (not field.null and field.blank) or (field.get_default() == ''):
                if field.empty_strings_allowed and self._get_connection().features.interprets_empty_strings_as_nulls:
                    sql += " DEFAULT ''"
                # Error here would be nice, but doesn't seem to play fair.
                #else:
                #    raise ValueError("Attempting to add a non null column that isn't character based without an explicit default value.")

        if field.rel and self.supports_foreign_keys:
            # HACK: "soft" FK handling begin
            if not hasattr(field, 'no_db_constraints') or not field.no_db_constraints:
                self.add_deferred_sql(
                    self.foreign_key_sql(
                        table_name,
                        field.column,
                        field.rel.to._meta.db_table,
                        field.rel.to._meta.get_field(field.rel.field_name).column
                    )
                )
            # HACK: "soft" FK handling end

    # Things like the contrib.gis module fields have this in 1.1 and below
    if hasattr(field, 'post_create_sql'):
        for stmt in field.post_create_sql(no_style(), table_name):
            self.add_deferred_sql(stmt)
    
    # In 1.2 and above, you have to ask the DatabaseCreation stuff for it.
    # This also creates normal indexes in 1.1.
    if hasattr(self._get_connection().creation, "sql_indexes_for_field"):
        # Make a fake model to pass in, with only db_table
        model = self.mock_model("FakeModelForGISCreation", table_name)
        for stmt in self._get_connection().creation.sql_indexes_for_field(model, field, no_style()):
            self.add_deferred_sql(stmt)
    
    if sql:
        return sql % sqlparams
    else:
        return None

@invalidate_table_constraints
def alter_column(self, table_name, name, field, explicit_name=True, ignore_constraints=False):
    """
    Alters the given column name so it will match the given field.
    Note that conversion between the two by the database must be possible.
    Will not automatically add _id by default; to have this behavour, pass
    explicit_name=False.

    @param table_name: The name of the table to add the column to
    @param name: The name of the column to alter
    @param field: The new field definition to use
    """
    
    if self.dry_run:
        if self.debug:
            print '   - no dry run output for alter_column() due to dynamic DDL, sorry'
        return

    # hook for the field to do any resolution prior to it's attributes being queried
    if hasattr(field, 'south_init'):
        field.south_init()

    # Add _id or whatever if we need to
    field.set_attributes_from_name(name)
    if not explicit_name:
        name = field.column
    else:
        field.column = name

    if not ignore_constraints:
        # Drop all check constraints. Note that constraints will be added back
        # with self.alter_string_set_type and self.alter_string_drop_null.
        if self.has_check_constraints:
            check_constraints = self._constraints_affecting_columns(table_name, [name], "CHECK")
            for constraint in check_constraints:
                self.execute(self.delete_check_sql % {
                    'table': self.quote_name(table_name),
                    'constraint': self.quote_name(constraint),
                })
                
        # Drop or add UNIQUE constraint
        unique_constraint = list(self._constraints_affecting_columns(table_name, [name], "UNIQUE"))
        if field.unique and not unique_constraint:
            self.create_unique(table_name, [name])
        elif not field.unique and unique_constraint:
            self.delete_unique(table_name, [name])
    
        # Drop all foreign key constraints
        try:
            self.delete_foreign_key(table_name, name)
        except ValueError:
            # There weren't any
            pass

    # First, change the type
    params = {
        "column": self.quote_name(name),
        "type": self._db_type_for_alter_column(field),            
        "table_name": table_name
    }

    # SQLs is a list of (SQL, values) pairs.
    sqls = []
    
    # Only alter the column if it has a type (Geometry ones sometimes don't)
    if params["type"] is not None:
        sqls.append((self.alter_string_set_type % params, []))
    
    # Add any field- and backend- specific modifications
    self._alter_add_column_mods(field, name, params, sqls)
    # Next, nullity
    if field.null:
        sqls.append((self.alter_string_set_null % params, []))
    else:
        sqls.append((self.alter_string_drop_null % params, []))

    # Next, set any default
    self._alter_set_defaults(field, name, params, sqls)

    # Finally, actually change the column
    if self.allows_combined_alters:
        sqls, values = zip(*sqls)
        self.execute(
            "ALTER TABLE %s %s;" % (self.quote_name(table_name), ", ".join(sqls)),
            flatten(values),
        )
    else:
        # Databases like e.g. MySQL don't like more than one alter at once.
        for sql, values in sqls:
            self.execute("ALTER TABLE %s %s;" % (self.quote_name(table_name), sql), values)
    
    if not ignore_constraints:
        # Add back FK constraints if needed
        if field.rel and self.supports_foreign_keys:
            # HACK: "soft" FK handling begin
            if not hasattr(field, 'no_db_constraints') or not field.no_db_constraints:
                self.execute(
                    self.foreign_key_sql(
                        table_name,
                        field.column,
                        field.rel.to._meta.db_table,
                        field.rel.to._meta.get_field(field.rel.field_name).column
                    )
                )
            # HACK: "soft" FK handling end


# monkey patch South here
DatabaseOperations.alter_column = alter_column
DatabaseOperations.column_sql = column_sql


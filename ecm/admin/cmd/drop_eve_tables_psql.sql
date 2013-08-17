-- Copyright (c) 2010-2013 Robin Jarry
--
-- This file is part of EVE Corporation Management.
--
-- EVE Corporation Management is free software: you can redistribute it and/or
-- modify it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or (at your
-- option) any later version.
--
-- EVE Corporation Management is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
-- or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
-- more details.
--
-- You should have received a copy of the GNU General Public License along with
-- EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

BEGIN;

-- First we check if the 'plpgsql' language is installed
CREATE OR REPLACE FUNCTION create_language_plpgsql()
RETURNS BOOLEAN AS $$
    CREATE LANGUAGE plpgsql;
    SELECT TRUE;
$$ LANGUAGE SQL;

SELECT CASE WHEN NOT
    (
        SELECT  TRUE AS exists
        FROM    pg_language
        WHERE   lanname = 'plpgsql'
        UNION
        SELECT  FALSE AS exists
        ORDER BY exists DESC
        LIMIT 1
    )
THEN
    create_language_plpgsql()
ELSE
    FALSE
END AS plpgsql_created;

DROP FUNCTION create_language_plpgsql();

-- Then create a function that will drop tables
CREATE OR REPLACE FUNCTION drop_tables_not_like(IN _schema TEXT, IN _pattern TEXT)
RETURNS void
LANGUAGE plpgsql
AS
$$
DECLARE
    row     record;
BEGIN
    FOR row IN
        SELECT
            table_name
        FROM
            information_schema.tables
        WHERE
            table_type = 'BASE TABLE'
          AND
            table_schema = _schema
          AND
            table_name NOT LIKE _pattern
    LOOP
        EXECUTE 'DROP TABLE ' || quote_ident(_schema) || '.' || quote_ident(row.table_name);
        RAISE INFO 'Dropped table: %', quote_ident(_schema) || '.' || quote_ident(row.table_name);
    END LOOP;
END;
$$;

-- Finally drop tables
SELECT drop_tables_not_like(current_schema(), E'%\\_%');

-- and remove function
DROP FUNCTION drop_tables_not_like(IN _schema TEXT, IN _pattern TEXT);

COMMIT;

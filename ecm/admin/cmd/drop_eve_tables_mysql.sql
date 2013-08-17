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

-- Extend group_concat size limit (standard is 1024)
SET SESSION group_concat_max_len = 1024 * 200;

-- Generate drop command and assign to variable
SELECT CONCAT('DROP TABLE ', GROUP_CONCAT(TABLE_NAME), ';') INTO @dropcmd
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = (SELECT DATABASE() FROM DUAL)
AND TABLE_NAME NOT LIKE '%\_%';

-- Drop tables
PREPARE str FROM @dropcmd;
EXECUTE str;
DEALLOCATE PREPARE str;

COMMIT;

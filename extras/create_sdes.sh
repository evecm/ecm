#!/bin/sh

if [ -z "$1" ]; then
#                        $1      $2 $3   $4  $5
	echo 'create_sdes.sh ecminst db user pwd dumpprefix'
    echo 'NOTE: MySQL ECM instance required!'
	exit
fi

TABLES="eve_celestialobject eve_blueprintreq eve_blueprinttype eve_controltowerresource eve_marketgroup eve_type eve_group eve_category eve_skillreq"

# Dump the mysql from the ECM instance
ecm-admin dump $1 $5.mysql
bzip2 $5.mysql

# Dump json from the ECM instance
ecm-admin dump $1 $5.json --json
bzip2 $5.json

# Dump PostgreSQL from the ECM database
echo "BEGIN;" > $5.pgsql
cat > mysql2psql.yml <<EOL
mysql:
 hostname: localhost
 port: 3306
 socket: /var/run/mysqld/mysqld.sock
 database: $2
 username: $3
 password: $4
destination:
 file: out.pgsql
supress_data: false
supress_ddl: true
force_truncate: true
index_prefix: index
only_tables:
EOL
for table in $TABLES
do
    echo "- $table" >> mysql2psql.yml
done

# Must have py-mysql2pgsql installed (as well as PostgreSQL itself)
py-mysql2pgsql -v -f mysql2psql.yml
cat out.pgsql >> $5.pgsql
echo "COMMIT;" >> $5.pgsql

# Cleanup
rm out.pgsql
rm mysql2psql.yml
bzip2 $5.pgsql

# Convert mysql to sqlite
./mysql2sqlite.sh --default-character-set=utf8 -u $3 --password=$4 $2 $TABLES | sqlite3 $5.sqlite
bzip2 $5.sqlite

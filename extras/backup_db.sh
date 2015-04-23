#!/bin/sh

if [ -z "$1" ]; then
#                          $1 $2   $3  $4
	echo 'backup_db.sh db user pwd file'
	exit
fi

mysqldump -u $2 --password=$3 --ignore-table=$1.eve_blueprintreq --ignore-table=$1.eve_blueprinttype --ignore-table=$1.eve_category --ignore-table=$1.eve_celestialobject --ignore-table=$1.eve_controltowerresource --ignore-table=$1.eve_group --ignore-table=$1.eve_marketgroup --ignore-table=$1.eve_skillreq --ignore-table=$1.eve_type $1 > $4


#TABLES="eve_celestialobject eve_blueprintreq eve_blueprinttype eve_controltowerresource eve_marketgroup eve_type eve_group eve_category eve_skillreq"

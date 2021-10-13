#!/bin/bash
# Returns only the number of job records
FULLPATH="$(dirname $(realpath $0))"
res="`sudo mysql -u root < $FULLPATH/count_jobrecords.sql`"
sed -n '2p' <<< $res

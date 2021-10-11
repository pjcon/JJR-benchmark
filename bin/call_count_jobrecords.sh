#!/bin/bash
# Returns only the number of job records
res=`sudo mysql -u root < count_jobrecords.sql`
sed -n '2p' <<< $res

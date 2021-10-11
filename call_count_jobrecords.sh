#!/bin/bash
res=`sudo mysql -u root < count_jobrecords.sql`
sed -n '2p' <<< $res

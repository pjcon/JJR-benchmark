#!/bin/bash

if [[ -z $1 ]]; then
    echo "Usage: $0 (all|new)"
else if [[ $1 == 'new' ]]; then
    $DEL='delete_new_data.sql'
else if [[ $1 == 'all ']]; then
    $DEL='delete_all_data.sql'
fi

sudo mysql -u root < $DEL

#!/bin/bash

if [[ $1 == 'new' ]]; then
    $DEL='delete_new_data.sql'
else;
    $DEL='delete_all_data.sql'
fi

sudo mysql -u root < $DEL

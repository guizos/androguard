#!/bin/bash

ls -Alrt -d -1 $PWD/scripts/{*,.*} | grep 'intent_actions' > file_names
while read p; do
  cat $p >> temp_intents
done <file_names

grep -v -f temp_intents $1


rm file_names

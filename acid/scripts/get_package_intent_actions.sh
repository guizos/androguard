#!/bin/bash

grep $1 mcafee_results_trans_intent_result_* | cut -d , -f 2 | cut -c 2- | rev | cut -c 4- | rev | sort | uniq

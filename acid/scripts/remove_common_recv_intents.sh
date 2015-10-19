#!/bin/bash


grep -v -f acid/results/intent_data/common_intent_actions $1 | grep -v -f acid/results/intent_data/google_intent_actions 

#!/bin/bash

if [ `date +%H:%M` == "06:15" ]
then
    echo "***REMOVED******REMOVED*** Cronjob Started ***REMOVED******REMOVED******"

    python ${OPENSHIFT_REPO_DIR}/scraper/main.py

    echo "***REMOVED******REMOVED*** Cronjob Executed ***REMOVED******REMOVED******"
fi



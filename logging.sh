#!/bin/bash

export NOW=$(date +"%Y%b%d_%H%M%S")
export LOGPATH=$SCRATCH/galaxy_srv/galaxy/var/gravity/log
mv $LOGPATH/gunicorn.log $SCRATCH/galaxy_log_backups/gunicorn_${NOW}.log
mv $LOGPATH/handler_0.log $SCRATCH/galaxy_log_backups/handler_0_${NOW}.log
mv $LOGPATH/handler_1.log $SCRATCH/galaxy_log_backups/handler_1_${NOW}.log
mv $LOGPATH/handler_2.log $SCRATCH/galaxy_log_backups/handler_2_${NOW}.log
mv $LOGPATH/handler_3.log $SCRATCH/galaxy_log_backups/handler_3_${NOW}.log
mv $LOGPATH/handler_4.log $SCRATCH/galaxy_log_backups/handler_4_${NOW}.log
echo Log back up done at `date`.
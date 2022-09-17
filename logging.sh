#!/bin/bash

export NOW=$(date +"%Y%b%d_%H%M%S")
export LOGPATH=$SCRATCH/galaxy_srv/galaxy/var/gravity/log
mv $SCRATCH/galaxy_srv/galaxy/var/gravity/log/gunicorn.log $SCRATCH/galaxy_log_backups/gunicorn_${NOW}.log
mv $SCRATCH/galaxy_srv/galaxy/var/gravity/log/handler_0.log $SCRATCH/galaxy_log_backups/handler_0_${NOW}.log
mv $SCRATCH/galaxy_srv/galaxy/var/gravity/log/handler_1.log $SCRATCH/galaxy_log_backups/handler_1_${NOW}.log
mv $SCRATCH/galaxy_srv/galaxy/var/gravity/log/handler_2.log $SCRATCH/galaxy_log_backups/handler_2_${NOW}.log
echo Log back up done at `date`.
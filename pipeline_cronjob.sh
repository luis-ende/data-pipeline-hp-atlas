#!/bin/bash

# Cronjob runs on server sil.supnapps.com

echo date
echo " - Executing HPA's data ingestion cron job..."
cd /opt/sas_hp_atlas/sas-human-protein-atlas
python3 main.py
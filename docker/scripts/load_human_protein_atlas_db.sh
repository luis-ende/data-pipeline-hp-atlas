#!/bin/bash

cd /opt/human-protein-atlas-scripts

psql -U atlas-admin -d human-protein-atlas -f create_schema.pgsql.sql
psql -U atlas-admin -d human-protein-atlas -f load_tables.pgsql.sql
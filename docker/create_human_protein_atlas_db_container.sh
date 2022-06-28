#!/bin/bash

ATLAS_TSV_PATH=$1
DB_PASSWORD=$2
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DOCKER_CONTEXT="${SCRIPT_DIR}"

# Build image first if it doesn't exist yet
atlas_image=$( docker images -q human_protein_atlas/postgres:latest )
if [[ -z "${atlas_image}" ]]; then
  echo "Building Docker image..."
  docker image build "$DOCKER_CONTEXT" -t human_protein_atlas/postgres
else
  echo "Removing currrent Docker container..."
  docker rm -f human-protein-atlas-postgres
fi

# DB Service will be available once the atlas data has been loaded from the TSV files
echo "Running new Docker container with bind source to '$ATLAS_TSV_PATH' ..."
docker run --name human-protein-atlas-postgres --restart=always \
  --mount type=bind,source="$ATLAS_TSV_PATH",target=/opt/human-protein-atlas-data \
  -p 7767:5432 \
  -e POSTGRES_USER=atlas-admin -e POSTGRES_PASSWORD="$DB_PASSWORD" -e POSTGRES_DB=human-protein-atlas \
  -d human_protein_atlas/postgres

# Remove all volumes not used by at least one container. -f without prompt
docker volume prune -f

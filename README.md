Human Protein Atlas Data Ingestion Pipeline

## Requirements:

  * Python 3.8+ 
  * Python libraries: configparser, csvkit ([csvsql](https://csvkit.readthedocs.io/en/latest/scripts/csvsql.html?highlight=csvsql)), bs4, pandas, zipfile, gzip
  * Docker 20.10+
  * [PostgreSQL official Docker image](https://hub.docker.com/_/postgres)
  * At least 50 GB free disk space (HPA 21.1)

## Pipeline execution

* Copy `pipeline.conf.example` over `pipeline.conf`
* Set the option `hp_atlas_single_entry_downloads_limit` under section `downloads_source` (`-1` to download all the single entries (more than 20000 files))
* Check and modify the `hp_atlas_downloads_index.json` file, which is a list of downloads the pipeline will extract and load       
* Make sure the section `[data_paths]` contains the right paths to working directories for the HPA uncompressed files. The pipeline won't keep the downloaded compressed files.
* Run the pipeline with the command: `python3 main.py` (or Run the project in PyCharm)
  * To run the pipeline to only download single entry files use: `python3 main.py --download-single-entries`
* Check if the Docker container `human-protein-atlas-postgres` is running and the status is up with: `docker ps` 
* Once the Docker container is running, use following command to connect to the Postgres instance via psql: 
`docker exec -it human-protein-atlas-postgres psql -U atlas-admin -d human-protein-atlas`
* To get a bash interactive shell for the running container use: `docker exec -it human-protein-atlas-postgres /bin/bash`
* The pipeline infers the latest version of the HPA by web scrapping the page: [https://www.proteinatlas.org/about/download](https://www.proteinatlas.org/about/download)

## Generated files

* The pipeline generates a version subfolder under the data directory (see `pipeline.conf`), e.g. 'v20', 'v21', where the uncompressed files, sample files, sql scripts and single entries are stored
  * Single entry files will also be stored under the data directory (version subfolder) in subfolders for each Ensembl Id (e.g. ENSG00000000457). A single entry directory can contain information about a Gene in different formats (xml, json, rdf, etc.)
  * The pipeline will only download formats defined in the `hp_atlas_single_entry_download_extensions` config option (see `pipeline.conf`)  
* To load HPA tsv files into Postgresql tables, the pipeline will generate sql schemas and load scripts (`.pgsql.sql`) under the data directory (version subfolder) based on the structure of the downloaded tsv files. This scripts will be executed when the Postgresql container (docker/scripts/load_human_protein_atlas_db.sh) is launched by the pipeline  
* A log file with the downloads information generated by the pipeline is stored under after the pipeline `./logs/latest_updates.json`
* Once the pipeline has been executed successfully it will update the `current_hp_atlas_version` configuration option (see `pipeline.conf`) to reflect the last HPA version used to update the HPA data store

## References

* [HPA Downloadable Data (latest version)](https://www.proteinatlas.org/about/download)
* [HPA Downloadable Data (e.g. for version 20: https://v20.proteinatlas.org/about/download)](https://v20.proteinatlas.org/about/download)
  * Also applies to single entries, e.g. use https://v20.proteinatlas.org/ENSG00000134057.xml to download version 20 of a single entry
* [Release history](https://v20.proteinatlas.org/about/releases)
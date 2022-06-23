import sys
import subprocess
import json
import configparser

cfg_parser = configparser.ConfigParser()
cfg_parser.read('pipeline.conf')


def load_postgresql_database(version_dir):
    hp_data_path = cfg_parser.get('data_paths', 'supernus_hp_data_path') + '/' + version_dir

    # Execute shell script to run a new docker container and
    # load the new version of the HPA downloads to the postgresql db
    print("Executing Docker container script.....")
    exit_code = subprocess.check_call("./docker/create_human_protein_atlas_db_container.sh %s %s" %
                                      (hp_data_path,
                                       cfg_parser.get('supernus_human_protein_atlas_db', 'db_password')),
                                      shell=True)
    print("Script executed. Exit code: " + str(exit_code))

import sys

from pipeline_helpers import get_version_dir_name
from extract_human_protein_atlas import get_hpa_latest_version, download_hpa_files, download_single_entries
from load_human_protein_atlas import load_postgresql_database
from log_pipeline_info import log_updates_info, update_config_info

import configparser

cfg_parser = configparser.ConfigParser()
cfg_parser.read('pipeline.conf')


def build_dp_human_protein_atlas():
    print('Fetching latest HPA version ................')
    latest_version = get_hpa_latest_version()
    if latest_version != cfg_parser.get('last_update', 'current_hp_atlas_version'):
        print('Downloading zip files - HPA v' + latest_version)
        downloads_info = download_hpa_files(latest_version)
        if downloads_info['download_status'] == 'success':
            print('Loading downloads into the database ................')
            version_directory = get_version_dir_name(latest_version)
            load_postgresql_database(latest_version, version_directory, downloads_info)
            update_config_info(downloads_info)
            if cfg_parser.get('pipeline_execution', 'always_download_single_entries') == "True":
                print('Downloading single entry files .....................................')
                download_single_entries(latest_version, version_directory)
        else:
            print('Download status is failed, pipeline stopped. Please check the logs.')

        print('Logging updates info .....................................')
        log_updates_info(downloads_info, 'latest_updates_file')
    else:
        print('No new version found. Pipeline finished.')
        # TODO: Add notifications via Email to provide information about errors


if __name__ == '__main__':
    current_version = cfg_parser.get('last_update', 'current_hp_atlas_version')
    if len(sys.argv) == 2 and sys.argv[1] == '--download-single-entries':
        print('Starting single entry files download .....................................')
        se_downloads_info = download_single_entries(current_version, get_version_dir_name(current_version))
        print('Logging updates info .....................................')
        log_updates_info(se_downloads_info, 'latest_single_entrie_updates')
    else:
        build_dp_human_protein_atlas()

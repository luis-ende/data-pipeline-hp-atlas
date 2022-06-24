from extract_human_protein_atlas import get_hpa_latest_version, download_hpa_files, download_single_entries
from load_human_protein_atlas import load_postgresql_database
from log_pipeline_info import log_updates_info, update_config_info


def build_supernus_human_protein_atlas():
    latest_version = get_hpa_latest_version()
    print('Downloading zip files - HPA v' + latest_version)
    downloads_info = download_hpa_files(latest_version)
    if downloads_info['download_status'] == 'success':
        print('Loading downloads into the database ................')
        version_directory = 'v' + latest_version[:latest_version.index(".")]
        load_postgresql_database(latest_version, version_directory, downloads_info)
        update_config_info(downloads_info)
        print('Downloading single entry files .....................................')
        download_single_entries(latest_version, version_directory)
    else:
        print('Download status is failed, pipeline stopped. Please check the logs.')

    print('Logging updates info .....................................')
    log_updates_info(downloads_info)
    # TODO: Add notifications via Email to provide information about errors


if __name__ == '__main__':
    build_supernus_human_protein_atlas()

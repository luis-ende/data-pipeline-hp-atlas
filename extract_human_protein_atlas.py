#! /usr/bin/env python3

import sys
import time
import os
import json
import pandas as pd
import zipfile
import requests
from datetime import datetime
from bs4 import BeautifulSoup

import configparser

HPA_RELEASES_URL = 'https://www.proteinatlas.org/about/releases'
HPA_DOWNLOAD_URL_PATTERN = 'https://v%s.proteinatlas.org/download/%s'
HPA_SINGLE_ENTRY_DOWNLOAD_URL_PATTERN = 'https://v%s.proteinatlas.org/%s.%s'

cfg_parser = configparser.ConfigParser()
cfg_parser.read('pipeline.conf')


def get_hpa_latest_version():
    # TODO: Implement Web Scraping to get the latest version number
    # atlas_releases_page = requests.get(HUMAN_PROTEIN_ATLAS_RELEASES_URL)
    # if atlas_releases_page.status_code == 200:
    #     atlas_releases_html = BeautifulSoup(atlas_releases_page.content, 'html.parser')
    #     # print(atlas_releases_html.prettify())

    return '21.1'


def download_hpa_files(version):
    date_format = '%Y-%m-%dT%H:%M:%S.000Z'
    downloads_info = {
        'version': version,
        'download_date': datetime.now().strftime(date_format),
        'download_status': 'success',
        'downloads': []
    }

    downloads_index = get_downloads_index()
    major_version = version[:version.index(".")]
    if len(downloads_index) > 0:
        if not os.path.exists('downloads'):
            os.mkdir('downloads')
        for download_data in downloads_index['downloads']:
            file_name = './downloads/' + download_data['file_name']
            download_url = HPA_DOWNLOAD_URL_PATTERN % (major_version, download_data['file_name'])
            file_download_status = 'success'
            file_stream = requests.get(download_url, stream=True)
            if file_stream.status_code != 200:
                file_download_status = 'failed'

            try:
                with open(file_name, 'wb') as f:
                    print("Downloading '%s - %s' from: %s" %
                          (download_data['atlas_download_number'], download_data['name'], download_url))
                    for chunk in file_stream.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                    print("File downloaded.")
            except:
                file_download_status = 'failed'

            downloads_info['downloads'].append({
                'download_file_url': download_url,
                'download_content_type': 'application/zip',
                'download_file_size': os.stat(file_name).st_size / (1024 * 1024),
                'download_date': datetime.now().strftime(date_format),
                'download_status': file_download_status
            })

            if file_download_status == 'failed':
                # Stop pipeline here if one file fails to download
                downloads_info['download_status'] = 'failed'
                return downloads_info

            time.sleep(2)

            unzip_downloaded_file(file_name, major_version)

    return downloads_info


def get_downloads_index():
    updates_log_file = cfg_parser.get('downloads_source', 'hp_atlas_downloads_index')
    downloads_index = {}
    if os.path.exists(updates_log_file):
        f = open(updates_log_file)
        downloads_index = json.load(f)
        f.close()

    return downloads_index


def unzip_downloaded_file(zip_update_file, version):
    hp_atlas_data_path = cfg_parser.get('data_paths', 'supernus_hp_data_path')
    if not os.path.exists(hp_atlas_data_path):
        sys.exit("Human Protein Atlas data directory doesn't exist: " + hp_atlas_data_path +
                 ". See [data_paths] section in config file.")

    version_directory = 'v' + version
    hp_atlas_data_version_path = hp_atlas_data_path + "/" + version_directory
    if not os.path.exists(hp_atlas_data_version_path):
        os.mkdir(hp_atlas_data_version_path)

    if os.path.exists(zip_update_file) and zipfile.is_zipfile(zip_update_file):
        with zipfile.ZipFile(zip_update_file, 'r') as zip_ref:
            print('Extracting file ' + zip_update_file + ' to ' + hp_atlas_data_path)
            zip_ref.extractall(hp_atlas_data_version_path)
            print('Zip file extracted.')
        os.remove(zip_update_file)
    else:
        print("Path doesn't exist or not valid zip file '" + zip_update_file + "'")
        sys.exit("[Error] Extraction of Human Protein Atlas zip file couldn't be completed successfully.")


def download_single_entries(version, version_dir):
    major_version = version[:version.index(".")]
    download_extensions = cfg_parser.get('downloads_source', 'hp_atlas_single_entry_download_extensions').split(',')
    hp_data_path = cfg_parser.get('data_paths', 'supernus_hp_data_path') + '/' + version_dir
    proteinatlas_tsv_path = hp_data_path + '/' + 'proteinatlas.tsv'
    # Set option to -1 in the configuration to download all files
    downloads_limit = int(cfg_parser.get('downloads_source', 'hp_atlas_single_entry_downloads_limit'))

    if not os.path.exists(proteinatlas_tsv_path):
        sys.exit("[Error] HPA '%s' file not found." % proteinatlas_tsv_path)

    proteinatlas_df = pd.read_csv(proteinatlas_tsv_path, sep='\t', header=0)
    ensembl_keys = proteinatlas_df.loc[:, "Ensembl"]
    downloads_count = 1
    for ensembl in ensembl_keys:
        ensembl_dir = hp_data_path + '/' + ensembl
        if not os.path.exists(ensembl_dir):
            os.mkdir(ensembl_dir)

        for download_extension in download_extensions:
            file_name = ensembl + '.' + download_extension
            file_path = ensembl_dir + '/' + file_name
            download_url = HPA_SINGLE_ENTRY_DOWNLOAD_URL_PATTERN % (major_version, ensembl, download_extension)
            file_stream = requests.get(download_url, stream=True)

            with open(file_path, 'wb') as f:
                print("Downloading '%s' from: %s" % (file_name, download_url))
                for chunk in file_stream.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                print("File '%s' downloaded (%d)." % (file_name, downloads_count))

        downloads_count += 1
        if downloads_limit != -1 and downloads_count > downloads_limit:
            break



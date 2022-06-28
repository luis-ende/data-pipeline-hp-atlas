#! /usr/bin/env python3
import re
import sys
import time
import os
import json
import pandas as pd
import zipfile
import gzip
import shutil
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from pipeline_helpers import get_version_dir_name, get_major_version

import configparser

HPA_DOWNLOADS_URL = 'https://www.proteinatlas.org/about/download'
HPA_DOWNLOAD_URL_PATTERN = 'https://v%s.proteinatlas.org/download/%s'
HPA_SINGLE_ENTRY_DOWNLOAD_URL_PATTERN = 'https://v%s.proteinatlas.org/%s.%s'
LOG_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
MAX_DOWNLOAD_RETRIES = 3

cfg_parser = configparser.ConfigParser()
cfg_parser.read('pipeline.conf')


def get_hpa_latest_version():
    version_number = '21.1'
    atlas_releases_page = requests.get(HPA_DOWNLOADS_URL)
    if atlas_releases_page.status_code == 200:
        atlas_releases_html = BeautifulSoup(atlas_releases_page.content, 'html.parser')
        # Find first ocurrence
        print('Searching for latest HPA version in %s' % HPA_DOWNLOADS_URL)
        version_text = atlas_releases_html.find(string=re.compile("Human Protein Atlas version"))
        if version_text:
            version_text = re.search(r'version\s*([\d.]+)', version_text).group(1)
            version_number = version_text.rstrip('.')

    return version_number


def download_hpa_files(version):
    downloads_info = {
        'version': version,
        'download_date': datetime.now().strftime(LOG_TIMESTAMP_FORMAT),
        'download_status': 'success',
        'downloads': []
    }

    downloads_index = get_downloads_index()
    if len(downloads_index) > 0:
        if not os.path.exists('downloads'):
            os.mkdir('downloads')
        for download_data in downloads_index['downloads']:
            file_name = './downloads/' + download_data['file_name']
            download_url = HPA_DOWNLOAD_URL_PATTERN % (get_major_version(version),
                                                       download_data['file_name'])
            file_download_status = 'success'
            file_stream = requests.get(download_url, stream=True)
            if file_stream.status_code != 200:
                file_download_status = 'failed'

            try:
                with open(file_name, 'wb') as f:
                    print("Downloading '%s - %s' from: %s" %
                          (download_data['atlas_download_number'],
                           download_data['name'], download_url))
                    for chunk in file_stream.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                    print("File downloaded.")
            except:
                file_download_status = 'failed'

            if file_download_status == 'failed':
                # Stop pipeline here if one file fails to download
                downloads_info['download_status'] = 'failed'
                return downloads_info

            time.sleep(2)

            download_file_size = os.stat(file_name).st_size
            dest_file_path = unzip_downloaded_file(file_name, version)

            downloads_info['downloads'].append({
                'download_file_url': download_url,
                'download_content_type': 'application/zip',
                'download_file_size': download_file_size,
                'download_date': datetime.now().strftime(LOG_TIMESTAMP_FORMAT),
                'download_status': file_download_status,
                'dest_file_name': os.path.basename(dest_file_path)
            })

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

    hp_atlas_data_version_path = hp_atlas_data_path + "/" + get_version_dir_name(version)
    if not os.path.exists(hp_atlas_data_version_path):
        os.mkdir(hp_atlas_data_version_path)

    # Remove .zip or .gz extension
    dest_file_name = os.path.splitext(os.path.basename(zip_update_file))[0]
    dest_file_path = hp_atlas_data_version_path + '/' + dest_file_name

    unzip_success = True
    if os.path.exists(zip_update_file):
        if zipfile.is_zipfile(zip_update_file):
            with zipfile.ZipFile(zip_update_file, 'r') as zip_ref:
                print('Extracting file ' + zip_update_file + ' to ' + hp_atlas_data_path)
                zip_ref.extractall(hp_atlas_data_version_path)
                print('Zip file extracted.')
        else:
            # Try extracting with gzip
            try:
                with gzip.open(zip_update_file, 'rb') as f_in:
                    print('Extracting file ' + zip_update_file + ' to ' + hp_atlas_data_path)
                    with open(dest_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                    print('Gzip file extracted.')
            except gzip.BadGzipFile:
                unzip_success = False
                print("File is not a valid gzip file '" + zip_update_file + "'")
    else:
        unzip_success = False
        print("Zip file path not found '" + zip_update_file + "'")

    if unzip_success:
        os.remove(zip_update_file)
    else:
        sys.exit("[Error] Extraction of Human Protein Atlas zip file couldn't be completed successfully.")

    return dest_file_path


def download_single_entries(version, version_dir):
    downloads_info = []
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
            if os.path.exists(file_path):
                print("File '%s' already exists. Skipping..." % file_path)
                continue

            download_url = HPA_SINGLE_ENTRY_DOWNLOAD_URL_PATTERN % (get_major_version(version),
                                                                    ensembl, download_extension)
            download_success = False
            download_retry_count = 1
            while not download_success and download_retry_count < MAX_DOWNLOAD_RETRIES:
                try:
                    file_stream = requests.get(download_url, stream=True)
                    with open(file_path, 'wb') as f:
                        print("Downloading '%s' from: %s" % (file_name, download_url))
                        for chunk in file_stream.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                        print("File '%s' downloaded (%d)." % (file_name, downloads_count))
                        download_success = True
                except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
                    download_success = False
                    download_retry_count += 1
                    if download_retry_count < MAX_DOWNLOAD_RETRIES:
                        print("Network Connection error. File couldn't be downloaded, "
                              "retrying again (%d) in 20 seconds..." % download_retry_count)
                        time.sleep(20)

            if not download_success:
                sys.exit("[Error] File couldn't be downloaded (retried %d times). Pipeline interrupted." %
                         download_retry_count)

            downloads_info.append({
                "ensembl_id": ensembl,
                "version": version,
                "esembl_file_name": file_name,
                "download_date": datetime.now().strftime(LOG_TIMESTAMP_FORMAT),
            })

        downloads_count += 1
        if downloads_limit != -1 and downloads_count > downloads_limit:
            return downloads_info

    # TODO: Implement auto recovery in case a download makes the pipeline fail and has to be restarted
    return downloads_info

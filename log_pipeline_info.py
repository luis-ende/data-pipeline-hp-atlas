import sys
import os
import json
import configparser
from datetime import datetime


cfg_parser = configparser.ConfigParser()
cfg_parser.read('pipeline.conf')


def log_updates_info(latest_updates, config_log_file_option):
    """
    Log applied updates (see pipeline.conf)
    """
    updates_log_file = cfg_parser.get('pipeline_log_paths', config_log_file_option)
    updates_list = []
    if os.path.exists(updates_log_file):
        f = open(updates_log_file)
        updates_list = json.load(f)
        f.close()

    updates_list.append(latest_updates)
    with open(updates_log_file, 'w') as outfile:
        json.dump(updates_list, outfile)


def update_config_info(latest_updates):
    cfg_parser.set('last_update', 'current_hp_atlas_version', latest_updates['version'])
    cfg_parser.set('last_update', 'downloads_last_update', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    with open('pipeline.conf', 'w') as configfile:
        cfg_parser.write(configfile)

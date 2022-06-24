import sys

import six
import os
import subprocess
import configparser
from csvkit.utilities.csvsql import CSVSQL

cfg_parser = configparser.ConfigParser()
cfg_parser.read('pipeline.conf')

MAX_TSV_COUNT_LINE = 500000
MAX_TSV_FILE_MB_SIZE = 1000

def create_posgresql_schema_file(version, version_dir, downloads_info):
    print("Generating Postgresql schemas...................")
    # Only process TSV files
    tsv_downloads_info = filter(lambda item: item['dest_file_name'].split('.')[-1] == 'tsv',
                                downloads_info['downloads'])

    sql_file_path = version_dir + '/create_schema.pgsql.sql'
    with open(sql_file_path, 'w') as f:
        f.write('-- HPA Version %s\n\n' % version)

    for download_file in tsv_downloads_info:
        print("Generating Postgresql schema for: " + download_file['dest_file_name'])
        output_file = six.StringIO()
        tsv_file_path = version_dir + '/' + download_file['dest_file_name']
        table_name = os.path.splitext(download_file['dest_file_name'])[0]
        if get_file_lines_count(tsv_file_path) > MAX_TSV_COUNT_LINE:
            # Tries creating a smaller sample file with fewer lines that can be handled by csvsql
            print("Generating sample file for: " + tsv_file_path)
            sample_lines_count = MAX_TSV_COUNT_LINE
            if os.stat(tsv_file_path).st_size / (1024 * 1024) > MAX_TSV_FILE_MB_SIZE:
                # For files greater than 1GB take just one line to sample
                sample_lines_count = 1
            tsv_file_path = create_sample_file(tsv_file_path, sample_lines_count)

        # -t tab delimited, -i dialect 'postgresql'
        schema_def = CSVSQL(['-t', '--no-constraints', '-i', 'postgresql', tsv_file_path], output_file)
        schema_def.main()
        schema_text = output_file.getvalue() + '\n\n'
        schema_text += "SELECT 'created table %s' AS progress;\n\n" % table_name
        print("Schema generated for: " + download_file['dest_file_name'])
        with open(sql_file_path, 'a') as f:
            f.write(schema_text + '\n')


def create_postgresql_load_file(version, version_dir, downloads_info):
    sql_file_path = version_dir + '/load_tables.pgsql.sql'
    # Only process TSV files
    tsv_downloads_info = filter(lambda item: item['dest_file_name'].split('.')[-1] == 'tsv',
                                downloads_info['downloads'])

    with open(sql_file_path, 'w') as f:
        f.write('-- HPA Version %s\n\n' % version)

    for download_file in tsv_downloads_info:
        # Remove file extension to form table name
        table_name = os.path.splitext(download_file['dest_file_name'])[0]
        load_statements = "SELECT 'loading data from %s' AS progress;\n\n" % download_file['dest_file_name']
        load_statements += "COPY %s\n" % table_name
        load_statements += "FROM '/opt/human-protein-atlas-data/%s'\n" % download_file['dest_file_name']
        load_statements += "DELIMITER E'\\t'\n"
        load_statements += "ENCODING 'utf-8'\n"
        load_statements += "CSV HEADER;\n\n"
        load_statements += "SELECT '%s' AS imported;\n\n" % table_name

        with open(sql_file_path, 'a') as f:
            f.write(load_statements)


def load_postgresql_database(version, version_dir, downloads_info):
    hpa_version_directory = cfg_parser.get('data_paths', 'supernus_hp_data_path') + '/' + version_dir
    # Generate create_schema.pgsql.sql
    create_posgresql_schema_file(version, hpa_version_directory, downloads_info)
    # Generate load_tables.pgsql.sql
    create_postgresql_load_file(version, hpa_version_directory, downloads_info)

    # Execute shell script to run a new docker container and
    # load the new version of the HPA tsv downloads to the postgresql db
    print("Executing Docker container script...............")
    exit_code = subprocess.check_call("./docker/create_human_protein_atlas_db_container.sh %s %s" %
                                      (hpa_version_directory,
                                       cfg_parser.get('supernus_human_protein_atlas_db', 'db_password')),
                                      shell=True)
    print("Script executed. Exit code: " + str(exit_code))


def get_file_lines_count(file_path):
    process = subprocess.Popen(['wc', '-l', file_path], stdout=subprocess.PIPE)
    lines_count = int(process.communicate()[0].decode('utf-8').split(' ')[0])

    return lines_count


def create_sample_file(file_path, sample_lines_count):
    file_path_elements = os.path.splitext(file_path)
    sample_file_path = '%s_sample%s' % (file_path_elements[0], file_path_elements[1])
    exit_code = subprocess.check_call('head -n %d %s > %s' %
                                      (sample_lines_count, file_path, sample_file_path), shell=True)

    if exit_code != 0:
        sample_file_path = file_path

    return sample_file_path



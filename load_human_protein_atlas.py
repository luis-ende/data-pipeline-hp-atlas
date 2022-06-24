import six
import os
import subprocess
import configparser
from csvkit.utilities.csvsql import CSVSQL

cfg_parser = configparser.ConfigParser()
cfg_parser.read('pipeline.conf')


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
        # -t tab delimited, -i dialect 'postgresql'
        schema_def = CSVSQL(['-t', '-i', 'postgresql', tsv_file_path], output_file)
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

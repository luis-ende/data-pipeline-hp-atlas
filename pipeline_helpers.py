def get_major_version(version):
    # Get major version for the name of the version directory (e.g. for 21.1 = 'v21')
    return version[:version.index(".")]


def get_version_dir_name(version):
    return 'v' + get_major_version(version)


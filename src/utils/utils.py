import os

def encode_file_path_properly (file_path) -> str:

    # make sure that '~' in filename is interpreted properly
    file_path = os.path.expanduser(file_path)

    # make sure path is absolute
    file_path = os.path.abspath(file_path)

    return file_path
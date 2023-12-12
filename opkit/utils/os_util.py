import os


def is_exist(path):
    return os.path.exists(path)


def create_file(f_path):
    """ 检查并创建文件 """
    if not isinstance(f_path, str):
        raise ValueError("f must be str, %s found", type(f_path))

    if not is_exist(f_path):
        dir_path = os.path.dirname(f_path)
        create_dir(dir_path)

        try:
            with open(f_path, 'w'):
                os.chmod(f_path, 0o666)
        except OSError as e:
            print("Failed to create file {}: {}".format(f_path, e))
    else:
        os.chmod(f_path, 0o666)


def create_dir(dir_path):
    """ 创建文件夹 """
    os.makedirs(dir_path, exist_ok=True)

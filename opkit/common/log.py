import datetime
import os
import logging
import shutil

from opkit.common.constants import (
    DEFAULT_LOG_FILE,
    DEFAULT_MODE,
    DEFAULT_ENCODING,
    DEFAULT_FORMAT,
    DEFAULT_LOG_DIR,
    TODAY_DIR
)
from opkit.utils.os_util import is_exist, create_file

__base_config = {
    "filename": DEFAULT_LOG_FILE,
    "filemode": DEFAULT_MODE,
    "level": logging.INFO,
    "encoding": DEFAULT_ENCODING,
    "format": DEFAULT_FORMAT
}

if not is_exist(DEFAULT_LOG_FILE):
    dir_path = os.path.dirname(DEFAULT_LOG_FILE)
    os.makedirs(dir_path, exist_ok=True)

    open(DEFAULT_LOG_FILE, "w")
    os.chmod(DEFAULT_LOG_FILE, 0o666)

logging.basicConfig(**__base_config)


def generate_opkit_log():
    u"""生成每日opkit日志"""
    return _generate_log("opkit.log")


def generate_grab_log():
    u"""生成每日grab日志"""
    return _generate_log("grab.log")


def _generate_log(log_name):
    u"""生成每日日志"""
    # 创建每日日志
    paths = [DEFAULT_LOG_DIR, *_today(), log_name]
    log = '/'.join(paths)
    create_file(log)

    # 创建today目录链接
    if os.path.exists(TODAY_DIR):
        os.unlink(TODAY_DIR)

    os.symlink(os.path.dirname(log), TODAY_DIR)

    return log


def _today():
    today = datetime.date.today()
    return [str(today.year), str(today.month), str(today.day)]


def get_today_dir():
    return '/'.join([DEFAULT_LOG_DIR, *_today()])

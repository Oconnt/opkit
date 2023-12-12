from opkit.common.constants import (
    DEFAULT_FORMAT,
)
from opkit.common.log import logging, generate_grab_log
from opkit.grab.handle.base import analysis


def output_log(name='grap_output_log', log_file=None,
               level=logging.INFO):
    """ 解析包后输出到指定日志文件 """
    def handler(pkg):
        lf = generate_grab_log() if not log_file else log_file

        # 解析包内容并转换为日志格式msg
        result = analysis(pkg)
        msg = conv_log(result)

        # 创建子日志文件
        logger = logging.getLogger(name)
        logger.propagate = False
        logger.setLevel(level)

        # 设置文件输出处理器
        file_handler = logging.FileHandler(lf)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))

        logger.addHandler(file_handler)

        logger.log(level, msg)

    return handler


def conv_log(d):
    def analysis_dict(data):
        line = "({})"
        attrs = []
        for k, v in data.items():
            attr = "{key}={val}"
            val = v if not isinstance(v, dict) else analysis_dict(v)
            attr = attr.format(key=k, val=val)
            attrs.append(attr)

        return line.format(", ".join(attrs))

    result = analysis_dict(d)
    return result

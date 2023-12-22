#!/usr/bin/python
from opkit.utils import common_util as cm_util


class BaseMonitor(object):

    MONITOR_NAME = None

    @classmethod
    def get_subclasses(cls):
        return cm_util.get_subclasses(cls,
                                      cm_util.get_package_modules(__package__))

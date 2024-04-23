import os
import tempfile
import pyrasite
import importlib

from opkit.common.constants import (
    SCRIPT_MOD,
    COMMAND_KEY_MAPPING,
    LOCALHOST,
    INJECTED
)
from opkit.kit.base import BaseManager
from opkit.kit.trace import task as trace_task
from opkit.kit.trace import script
from opkit.utils import os_util


class Manager(BaseManager):

    def __init__(self, pid):
        if not os_util.is_linux():
            raise SystemError('The system is not Linux.')

        self.pid = int(pid)
        self.ipc = pyrasite.PyrasiteIPC(self.pid)
        self._method = {
            'exec_script': self.exec_script,
            'read': self.read,
            'write_val': self.write_val,
            'dict_add': self.dict_add,
            'dict_del': self.dict_del,
            'list_append': self.list_append,
            'list_remove': self.list_remove,
            'object_set': self.object_set,
            'mem_view': self.mem_view,
            'rpdb_inject': self.rpdb_inject,
            'opkit_rpdb_inject': self.opkit_rpdb_inject,
        }

    @staticmethod
    def get_cmd(filename, **kwargs):
        path = '.'.join([SCRIPT_MOD, filename])
        mod = importlib.import_module(path)
        cmd = mod.script_content

        return cmd.format(**kwargs) if kwargs else cmd

    @staticmethod
    def convert_val(val):
        if isinstance(val, str):
            val = '"' + val + '"'

        return val

    def read(self, var):
        """
        读取进程变量值
        :param var: 变量名
        :return:
        """
        ret = self.exec('read', var=var)
        return ret

    def write_val(self, var, new_value):
        ret = self.exec('write_val', var=var, new_value=self.convert_val(new_value))  # noqa
        return ret

    def dict_add(self, var, key, new_value):
        ret = self.exec('dict_add', var=var, key=key, new_value=self.convert_val(new_value))  # noqa
        return ret

    def dict_del(self, var, key):
        ret = self.exec('dict_del', var=var, key=key)
        return ret

    def list_append(self, arr, var):
        ret = self.exec('list_append', arr=arr, var=self.convert_val(var))  # noqa
        return ret

    def list_remove(self, arr, var):
        ret = self.exec('list_remove', arr=arr, var=self.convert_val(var))  # noqa
        return ret

    def object_set(self, obj, var, new_value):
        ret = self.exec('object_set', obj=obj, var=self.convert_val(var), new_value=self.convert_val(new_value))  # noqa
        return ret

    def mem_view(self):
        ret = self.exec('mem_view')
        return ret

    def exec_script(self, script):
        with self.ipc as ipc:
            ret = ipc.cmd(script)

        return ret

    def rpdb_inject(self, port=0):
        cmd = self.get_cmd('rpdb_inject', port=port)
        fd, filename = tempfile.mkstemp()
        tmp = os.fdopen(fd, 'w')
        tmp.write(cmd)
        tmp.close()

        task = trace_task.InjectTask(self.pid, filename)
        task.start()

        prompt = 'pdb is running on %s:%d' % (LOCALHOST, port)
        print(prompt)

        task.join()

        # clear tmp file
        os.unlink(filename)

        return INJECTED

    def opkit_rpdb_inject(self, sock_file=None):
        if not sock_file:
            sock_file = '/tmp/rpdb_%d' % self.pid

        if os.path.exists(sock_file):
            os.remove(sock_file)

        cmd = self.get_cmd('opkit_rpdb_inject')
        fd, filename = tempfile.mkstemp()
        tmp = os.fdopen(fd, 'w')
        tmp.write(cmd)

        start_script = script.opkit_rpdb_inject_start_line.format(sock_file=sock_file)  # noqa

        tmp.write(start_script + '\n')
        tmp.close()

        task = trace_task.InjectTask(self.pid, filename)
        task.start()

        prompt = 'pdb is running on %s' % sock_file
        print(prompt)

        task.join()

        # clear tmp file
        os.unlink(filename)

        return INJECTED

    def exec(self, filename, **kwargs):
        with self.ipc as ipc:
            cmd = self.get_cmd(filename, **kwargs)
            ret = ipc.cmd(cmd)

        return ret

    def do(self, mode, *args):
        m = COMMAND_KEY_MAPPING.get(mode)
        func = self._method.get(m)
        if not func:
            raise Exception('No pattern exists')

        return func(*args)

import socket
import time
import pyrasite
import threading


class InjectTask(threading.Thread):

    def __init__(self, pid, filename, verbose=False, gdb_prefix=''):
        super(InjectTask, self).__init__(daemon=True)
        self.pid = pid
        self.filename = filename
        self.verbose = verbose
        self.gdb_prefix = gdb_prefix

    def run(self):
        pyrasite.inject(self.pid, self.filename, self.verbose, self.gdb_prefix)  # noqa


class ConnectPortTask(threading.Thread):

    def __init__(self, addr, port, timeout=2):
        super(ConnectPortTask, self).__init__(daemon=True)
        self.addr = addr
        self.port = port
        self.timeout = timeout

    def run(self):
        time.sleep(self.timeout)
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            skt.connect((self.addr, self.port))
        except ConnectionResetError:
            print("Connection to %s:%d refused." % (self.addr, self.port))
        finally:
            skt.close()


class ConnectUnixTask(threading.Thread):

    def __init__(self, sock_file, timeout=2):
        super(ConnectUnixTask, self).__init__(daemon=True)
        self.sock_file = sock_file
        self.timeout = timeout

    def run(self):
        time.sleep(self.timeout)
        skt = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            skt.connect(self.sock_file)
        except ConnectionResetError:
            print("Connection to %s refused." % self.sock_file)
        finally:
            skt.close()

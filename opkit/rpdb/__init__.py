"""Remote Python Debugger (pdb wrapper)."""

__author__ = "Occent <1825793535@qq.com>"
__version__ = "0.1.6"

import pdb
import socket
import threading
import signal
import sys
import os
import traceback
from functools import partial

# Get the current process ID
PID = os.getpid()
DEFAULT_SOCKET_FILE = '/tmp/rpdb_%s' % PID


class FileObjectWrapper(object):
    def __init__(self, fileobject, stdio):
        self._obj = fileobject
        self._io = stdio

    def __getattr__(self, attr):
        if hasattr(self._obj, attr):
            attr = getattr(self._obj, attr)
        elif hasattr(self._io, attr):
            attr = getattr(self._io, attr)
        else:
            raise AttributeError("Attribute %s is not found" % attr)
        return attr


class Rpdb(pdb.Pdb):

    def __init__(self, sock_file=DEFAULT_SOCKET_FILE):
        """Initialize the unix socket and initialize pdb."""
        self.sock_file = sock_file
        self.skt = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.skt.bind(self.sock_file)
        self.skt.listen(1)

        # Writes to stdout are forbidden in mod_wsgi environments
        try:
            sys.stderr.write("pdb is running on %s\n" % self.sock_file)
        except IOError:
            pass

        (clientsocket, address) = self.skt.accept()
        handle = clientsocket.makefile('rw')
        pdb.Pdb.__init__(self, completekey='tab',
                         stdin=FileObjectWrapper(handle, sys.__stdin__),
                         stdout=FileObjectWrapper(handle, sys.__stdout__))
        sys.stdout = sys.stdin = handle
        OCCUPIED.claim(self.sock_file, sys.stdout)

    def shutdown(self):
        """Revert stdin and stdout, close the socket."""
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__
        OCCUPIED.unclaim(self.sock_file)
        self.skt.close()

    def do_continue(self, arg):
        """Clean-up and do underlying continue."""
        try:
            return pdb.Pdb.do_continue(self, arg)
        finally:
            self.shutdown()

    do_c = do_cont = do_continue

    def do_quit(self, arg):
        """Clean-up and do underlying quit."""
        try:
            return pdb.Pdb.do_quit(self, arg)
        finally:
            self.shutdown()

    do_q = do_exit = do_quit

    def do_EOF(self, arg):
        """Clean-up and do underlying EOF."""
        try:
            return pdb.Pdb.do_EOF(self, arg)
        finally:
            self.shutdown()


def set_trace(sock_file=DEFAULT_SOCKET_FILE, frame=None):
    """Wrapper function to keep the same import x; x.set_trace() interface.

    We catch all the possible exceptions from pdb and cleanup.

    """
    try:
        debugger = Rpdb(sock_file)
    except socket.error:
        if OCCUPIED.is_claimed(sock_file, sys.stdout):
            # rpdb is already on this port - good enough, let it go on:
            sys.stdout.write("(Recurrent rpdb invocation ignored)\n")
            return
        else:
            # Port occupied by something else.
            raise
    try:
        debugger.set_trace(frame or sys._getframe().f_back)
    except Exception:
        traceback.print_exc()


def _trap_handler(sock_file, frame):
    set_trace(sock_file, frame=frame)


def handle_trap(sock_file):
    """Register rpdb as the SIGTRAP signal handler"""
    signal.signal(signal.SIGTRAP, partial(_trap_handler, sock_file))


def post_mortem(sock_file):
    debugger = Rpdb(sock_file)
    type, value, tb = sys.exc_info()
    traceback.print_exc()
    debugger.reset()
    debugger.interaction(None, tb)


class OccupiedUnix(object):
    """Maintain rpdb port versus stdin/out file handles.

    Provides the means to determine whether or not a collision binding to a
    particular port is with an already operating rpdb session.

    Determination is according to whether a file handle is equal to what is
    registered against the specified port.
    """

    def __init__(self):
        self.lock = threading.RLock()
        self.claims = {}

    def claim(self, skt_file, handle):
        self.lock.acquire(True)
        self.claims[skt_file] = id(handle)
        self.lock.release()

    def is_claimed(self, skt_file, handle):
        self.lock.acquire(True)
        got = (self.claims.get(skt_file) == id(handle))
        self.lock.release()
        return got

    def unclaim(self, skt_file):
        self.lock.acquire(True)
        if self.claims.get(skt_file):
            del self.claims[skt_file]
        self.lock.release()


# {port: sys.stdout} pairs to track recursive rpdb invocation on same port.
# This scheme doesn't interfere with recursive invocations on separate ports -
# useful, eg, for concurrently debugging separate threads.
OCCUPIED = OccupiedUnix()

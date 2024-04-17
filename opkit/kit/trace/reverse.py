from pyrasite.reverse import ReversePythonShell


class RpdbReversePythonShell(ReversePythonShell):

    def __init__(self, host='localhost', port=5555):
        super(RpdbReversePythonShell, self).__init__()
        self.host = host
        self.port = port

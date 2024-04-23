# 捕获调试器退出异常让进程继续执行
opkit_rpdb_inject_start_line = '''
import bdb
try:
    set_trace(sock_file="{sock_file}")
except bdb.BdbQuit:
    pass
'''

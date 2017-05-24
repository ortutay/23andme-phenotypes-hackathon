import os
import multiprocessing


max_requests = 5000
max_requests_jitter = 50
preload_app = True
proc_name = 'my_app'
threads = multiprocessing.cpu_count() * 4
workers = multiprocessing.cpu_count() * 2 + 1
bind = '0.0.0.0:%s' % os.environ['PORT']

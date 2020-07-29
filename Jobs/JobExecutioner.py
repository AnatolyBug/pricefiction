import time
from .FRTB import *


class Job:
    def __init__(self):
        pass

    def run(self,request):
        job = globals()[request['Job']]
        t_job_start = time.time()
        job(request).run()
        t_job_end = time.time()
        print(t_job_end-t_job_start)

import gitinterface as gi
import os
from multiprocessing import Process


if __name__ == "__main__":
    
    env = gi.GitApiParams

    py_proc = Process(target=gi.start,args=(env,))
    py_proc.start()
 

    py_proc.join()
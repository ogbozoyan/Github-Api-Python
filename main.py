import gitinterface as gi
import os
from multiprocessing import Process

if __name__ == "__main__":
    env = gi.setup()
    gi.add_by_name(env,"main.py")
    gi.add_by_name(env,"gitinterface.py")
    params = gi.GitApiParams
    py_proc = Process(target=gi.start, args=(params,))
    py_proc.start()

    py_proc.join()

import gitinterface as gi
import os
import threading

def open_max_prog():
    os.startfile("DatasetCollector_.exe")
    max_thread = threading.Thread(target=open_max_prog)
    max_thread.start()
    max_thread.join()


if __name__ == "__main__":

    env = gi.setup()
    gi.add_by_name(env,"main.py")
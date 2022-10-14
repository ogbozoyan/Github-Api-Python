from GitInterface import *


def open_max_prog():
    os.startfile("DatasetCollector_.exe")
    max_thread = threading.Thread(target=open_max_prog)
    max_thread.start()
    max_thread.join()


if __name__ == "__main__":

    env = setup()
    add_by_name(env, "main.py")
    add_by_name(env, "GitInterface.py")
    print(env.content)

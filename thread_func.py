import threading

def thread_func(func, *args):
    Thread=threading.Thread(target=func, args=args,daemon=True)
    Thread.start()
import time, threading

def get_scores(url):
    time.sleep(1)
    return True

def execute_delay():
    time.sleep(2)

a = [1, 2, 3]
while a:
    start = time.time()

    t1 = threading.Thread(target=get_scores, args=('t'))
    t2 = threading.Thread(target=time.sleep(2), args=())

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"Finished {a.pop}: {time.time() - start}")


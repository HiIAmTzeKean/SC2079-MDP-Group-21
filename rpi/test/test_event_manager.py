import multiprocessing
import time

def set_event(event):
    time.sleep(2)
    event.set()
    print("Event is set.")

def wait_for_event(event):
    print("Waiting for event to be set...")
    event.wait()
    print("Event has been set.")

if __name__ == "__main__":
    event = multiprocessing.Event()

    p1 = multiprocessing.Process(target=set_event, args=(event,))
    p2 = multiprocessing.Process(target=wait_for_event, args=(event,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
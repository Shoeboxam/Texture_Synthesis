from multiprocessing.managers import BaseManager
from multiprocessing import Queue, Process, cpu_count, Lock
import time

from collections import defaultdict
from multiprocessing.managers import DictProxy


class DictManager(BaseManager):
    pass

DictManager.register('defaultdict', defaultdict, DictProxy)


def vectorize(items, function, args, returns=False):

    file_queue = Queue()
    map(file_queue.put, items)

    if returns:
        manager = DictManager()
        manager.start()
        accumulator = manager.defaultdict(list)

        args.append(Lock())
        args.append(accumulator)

    pool = [Process(target=process_wrapper, args=(file_queue, args), name=str(proc))
            for proc in range(cpu_count())]

    for proc in pool:
        proc.start()

    while not file_queue.empty():
        time.sleep(1)

    for proc in pool:
        proc.terminate()

    if returns:
        return accumulator


def process_wrapper(item_queue, function, arguments):
    while True:
        function(item_queue.get(), *arguments)

from multiprocessing.managers import BaseManager
from multiprocessing import Queue, Process, cpu_count
import time

from collections import defaultdict
from multiprocessing.managers import DictProxy


class DictManager(BaseManager):
    pass

DictManager.register('defaultdict', defaultdict, DictProxy)


def vectorize(items, function, arguments):

    file_queue = Queue()
    map(file_queue.put, items)

    pool = [Process(target=process_wrapper, args=arguments.prepend(file_queue), name=str(proc))
            for proc in range(cpu_count())]

    for proc in pool:
        proc.start()

    while not file_queue.empty():
        time.sleep(1)

    for proc in pool:
        proc.terminate()


def process_wrapper(item_queue, function, arguments):
    while True:
        function(item_queue.get(), *arguments)


def process_wrapper_managed(item_queue, function, arguments, lock, manager):
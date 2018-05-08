# -*- coding:utf-8 -*-
import random
import time
import threading


class BlockingQueue(object):

    '''
        注意：这个只是一个简易版的 BlockingQueue，e.g. 这个BlockingQueue
        is only suitable for one-producer-one-consumer problem.
        reference: https://en.wikipedia.org/wiki/Producer–consumer_problem
    '''
    def __init__(self, max_size=730*10):
        self.max_size = max_size
        self.datas = []
        self.elem_count = 0

    def put(self, token):
        if self.is_full():
            return
        #  由于只可能会有一个consumer和一个producer
        #  因此无需将append和after_put放在一个原子操作里面
        self.datas.append(token)
        self.elem_count += 1

    def pop(self):
        if self.is_empty():
            return
        result = self.datas.pop(0)
        self.elem_count -= 1
        return result

    def is_empty(self):
        return self.elem_count == 0

    def is_full(self):
        return self.elem_count == self.max_size

    def qsize(self):
        return len(self.datas)

    def after_put(self):
        if self.elem_count > self.max_size:
            return
        self.elem_count += 1

    def after_pop(self):
        if self.elem_count < 0:
            return
        self.elem_count -= 1


def test():
    def consumer_func(q):
        while True:
            while q.is_empty():
                time.sleep(random.random())
            token = q.pop()
            print token

    def producer_func(q):
        while True:
            while q.is_full():
                time.sleep(random.random())
            token = random.randint(1, 10)
            queue.put(token)

    queue = BlockingQueue()
    consumer = threading.Thread(target=consumer_func, args=(queue,))
    producer = threading.Thread(target=producer_func, args=(queue,))
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()


if __name__ == "__main__":
    test()
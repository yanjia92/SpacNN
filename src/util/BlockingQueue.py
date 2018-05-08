# -*- coding:utf-8 -*-


class BlockingQueue(object):

    '''
        注意：这个只是一个简易版的 BlockingQueue，e.g. 这个BlockingQueue
        is only suitable for one-producer-one-consumer problem.
        reference: https://en.wikipedia.org/wiki/Producer–consumer_problem
    '''
    def __init__(self, max_size=730):
        self.max_size = max_size
        self.datas = []
        self.fill_count = 0
        self.empty_count = max_size


    def put(self, token):
        if self.is_full():
            return
        self.datas.append(token)
        self.fill_count += 1
        self.empty_count -= 1

    def pop(self):
        if self.is_empty():
            return None
        self.empty_count += 1
        self.fill_count -= 1
        return self.datas.pop()

    def is_empty(self):
        return self.fill_count == 0

    def is_full(self):
        return self.empty_count == 0

    def qsize(self):
        return len(self.datas)

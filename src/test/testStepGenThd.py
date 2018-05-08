# -*- coding: utf-8 -*-
from model.ModelFactory import ModelFactory
from util.AnnotationHelper import profileit


model = ModelFactory.get_parsed(duration=1000000)
model.prepare_commands()

#  测试将队列填满需要多少时间
@profileit("stepgentime")
def test():
    step_gen = model.gen_next_step(passed_time=0.0)
    for _ in range(73000):
        step = next(step_gen)
        model.steps_queue.append(step)


if __name__ == "__main__":
    test()

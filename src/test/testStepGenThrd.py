from module.ModulesFile import StepGenThd
from model.ModelFactory import ModelFactory

def test():
    model = ModelFactory.get_built()
    model.duration = 730
    model.prepare()
    thrd = StepGenThd(model.gen_next_step(), model.steps_queue)
    thrd.start()
    thrd.join()
    print model.steps_queue.qsize()


if __name__ == "__main__":
    test()
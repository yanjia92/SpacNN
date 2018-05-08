from module.ModulesFile import StepGenThrd
from model.ModelFactory import ModelFactory

def test():
    model = ModelFactory.get_built()
    model.duration = 730
    model.prepare_commands()
    thrd = StepGenThrd(model.gen_next_step(), model.steps_queue)
    thrd.start()
    thrd.join()
    print model.steps_queue.qsize()


if __name__ == "__main__":
    test()
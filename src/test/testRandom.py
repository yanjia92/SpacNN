import random


def test():
    random.seed()
    print random.random()
    random.seed()
    print random.random()


if __name__ == "__main__":
    test()


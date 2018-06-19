def out(obj):
    def inner():
        print obj
    return inner


def local_func_test():
    for _ in range(2):
        def f():
            print 1
        print id(f)


def loop_func_test():
    from random import Random
    fs = []
    for _ in range(2):
        rnd = Random().randint(0,2)
        def f():
            print rnd
        fs.append(f)

    for f in fs:
        f()

def main():
    # obj = "q"
    # f1 = out(obj)
    # obj = "p"
    # f2 = out(obj)
    # f1()
    # f2()
    # local_func_test()
    loop_func_test()


if __name__ == "__main__":
    main()
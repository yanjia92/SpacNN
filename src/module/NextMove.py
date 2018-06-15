from collections import namedtuple

fileds = [
    "passed_time",
    "holding_time",
    "cmds",
    "exit_rate",
    "biasing_exit_rate"
]

NextMove = namedtuple("NextMove", fileds)
# allow default value for NextMove
NextMove.__new__.__defaults__ = (None, 0.0, list(), 0.0, 0.0)


def test():
    next_move = NextMove(passed_time=1)


if __name__ == "__main__":
    test()


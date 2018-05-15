# class NextMove(object):
#     def __init__(
#             self,
#             passed_time,
#             holding_time=0.0,
#             cmd=None,
#             exit_rate=None,
#             biasing_exit_rate=None):
#         self.cmd = cmd
#         self.holding_time = holding_time
#         self.passed_time = passed_time
#         self.exit_rate = exit_rate
#         self.biasing_exit_rate = biasing_exit_rate


from collections import namedtuple

fileds = [
    "passed_time",
    "holding_time",
    "cmd",
    "exit_rate",
    "biasing_exit_rate"
]

NextMove = namedtuple("NextMove", fileds)
# allow default value for NextMove
NextMove.__new__.__defaults__ = (None, 0.0, None, 0.0, 0.0)


def test():
    next_move = NextMove(passed_time=1)


if __name__ == "__main__":
    test()


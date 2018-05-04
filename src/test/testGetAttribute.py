class A(object):
    def __init__(self,a):
        self.a = a


class B(object):
    def __init__(self, b):
        self.b = b


class C(object):
    def __init__(self, a, b):
        self.instanceA = a
        self.instanceB = b
        self.map = dict()
        # self.map["instanceA"] = self
        # self.map["instanceB"] = self

        self.map['a'] = self.instanceA
        self.map['b'] = self.instanceB

    def __getattribute__(self, item):
        try:
            result = object.__getattribute__(self, item)
        except Exception as e:
            owner = self.map[item]
            if owner:
                result = object.__getattribute__(owner, item)
        finally:
            return result

def test():
    a = A(1)
    b = B(2)
    c = C(a, b)
    print c.a
    print c.b
    # d = dict()
    # print d is not None


if __name__ == "__main__":
    test()
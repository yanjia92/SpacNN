def test():
    sets = []
    es = set()
    sets.append(es)
    sets.append(set(["failure"]))
    s = set(["failure"])
    print s in sets
    print id(s) == id(sets[1])


if __name__ == "__main__":
    test()

import re

pattern = r"[\+\-]?\d+\.?\d*"
patternobj = re.compile(pattern)

testcases = (
    ("123", True),
    ("123.123", True),
    ("+123", True),
    ("-123", True),
    ("+-123", False),
    (".123", False),
    ("0.123", True)
)

def test():
    for case in testcases:
        if (patternobj.match(case[0]) is not None) != case[1]:
            print case[0], case[1]


if __name__ == "__main__":
    test()

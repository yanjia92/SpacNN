def rmcomment(line):
    found = line.find(r"//")
    if found == -1:
        return line.strip()
    return line[:found].strip()

def testrmcomment():
    testcases = (
        ("abc; //abc", "abc;"),
        ("abc; ", "abc;")
    )

    for case in testcases:
        if rmcomment(case[0]) != case[1]:
            print case[0], case[1]

if __name__ == "__main__":
    testrmcomment()


from util.MathUtils import rel_index
from util.CsvFileHelper import parse_csv_rows

path1 = "../test/unittest/no_anti.txt"
path2 = "../test/unittest/anti.txt"


def relative_index(path):
    rows = parse_csv_rows(path, types=int, has_headers=False)
    rows = map(lambda l: l[0], rows)
    arr1 = rows[0::2]
    arr2 = rows[1::2]
    return rel_index(arr1, arr2)


print relative_index(path1)
print relative_index(path2)


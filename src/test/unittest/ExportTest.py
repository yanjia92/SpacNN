import unittest
from util.CsvFileHelper import write_csv_rows


class ExportUnitTest(unittest.TestCase):
    def setUp(self):
        self.xs = [(1, 2), (2, 3)]
        self.ys = [2, 3]
        self.header = ["h1", "h2", "result"]
        self.datas = []
        for index, y in enumerate(self.ys):
            row = []
            row.extend(self.xs[index])
            row.append(y)
            self.datas.append(row)

    def test(self):
        export_to = "/Users/bitbook/Documents/export_to.csv"
        write_csv_rows(export_to, self.datas, self.header)


if __name__ == "__main__":
    unittest.main()


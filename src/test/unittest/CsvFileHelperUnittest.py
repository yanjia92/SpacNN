from unittest import TestCase
from util.CsvFileHelper import write_csv_rows, parse_csv_rows


class CsvFileHelperTest(TestCase):
    def setUp(self):
        self.write_to_path = "/Users/bitbook/Documents/temp.csv"
        self.headers = ["col1", "col2", "col3"]
        self.datas = []
        for _ in range(3):
            self.datas.append(map(float, range(3)))

    def test_write_read(self):
        write_csv_rows(self.write_to_path, datas=self.datas, headers=self.headers)
        rows = parse_csv_rows(self.write_to_path, float)
        for row1, row2 in zip(rows, self.datas):
            for item1, item2 in zip(row1, row2):
                self.assertEqual(item1, item2)


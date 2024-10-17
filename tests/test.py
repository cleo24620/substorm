import unittest
from substorm import config, data


class MyTestCase(unittest.TestCase):
    def test_columns_names(self):
        fp = r"\\Diskstation1\file_three\Alfven wave\OMNIData\omni_min201904.asc"  # assume already download the original data file
        df = data.csv2df(fp)
        self.assertEqual(list(df.columns), config.preprocess_omnidata_kwargs['specify_vars_rename'], "the names of rename columns are different from the preprocess_omnidata_kwargs['specify_vars_rename']")  # add assertion here


if __name__ == '__main__':
    unittest.main()

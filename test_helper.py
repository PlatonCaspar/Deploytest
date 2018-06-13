import unittest
import helper


class TestHelperMethods(unittest.TestCase):
    
    def test_array_max_val(self):
        a = [10001, 10002, 3, 4, 10005, 6, 10, 7, 8, 9]
        res = helper.array_max_val(a, "SDI")
        assert res is 10005
        res = helper.array_max_val(a, "IPE")        
        assert res is 10
        a = []
        res = helper.array_max_val(a, "SDI")
        assert res == 10000
        

if __name__ == '__main__':
    unittest.main()

        
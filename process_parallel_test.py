import unittest
from src.process_parallel import *

class TestParallel(unittest.TestCase):
    def test_parallel(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_parallel(func, args)
        assert results[1] == [func(*arg) for arg in args]

    def test_parallel_timeout(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_parallel(func, args, timeout = 5)
        assert results[1] == [func(*arg) for arg in args]

    def test_parallel_error(self):
        def func(x,y):
            raise Exception("Testing case where exception is thrown")

        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_parallel(func, args, timeout = 5)
        # assert results[1] == [func(*arg) for arg in args]

class TestFirst(unittest.TestCase):
    def test_first(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_first(func, args)
        assert results[1][0] in [func(*arg) for arg in args]

    def test_parallel_timeout(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_first(func, args, timeout = 5)
        assert results[1][0] in [func(*arg) for arg in args]

    
if __name__ == "__main__":
    unittest.main()
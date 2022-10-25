import unittest
from src.process_parallel import *

class TestParallel(unittest.TestCase):
    def test_parallel(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_parallel(func, args)
        assert results == [func(*arg) for arg in args]

    def test_parallel_timeout(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_parallel(func, args, timeout = 5)
        assert results == [func(*arg) for arg in args]

    def test_parallel_error(self):
        def func(x,y):
            raise Exception("Testing case where exception is thrown")

        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_parallel(func, args, timeout = 5)
        assert results == [None]*len(args) # ensure results are None
        
    def test_parallel_wrong_func(self):
        func = "A"

        args = [[1,2], [3,4], [5,6], [7,8]]
        try:
            results = process_parallel(func, args, timeout = 5)
        except Exception as e:
            isinstance(e, AssertionError) # check that the error gets caught in assertion
            
    def test_parallel_wrong_args(self):
        func = lambda x,y: x*y

        args = [[1,2], 3,4, 5,6, [7,8]]
        try:
            results = process_parallel(func, args, timeout = 5)
        except Exception as e:
            isinstance(e, AssertionError) # check that the error gets caught in assertion   

            
class testProcessParallelMultifunc(unittest.TestCase):
    def test_process_parallel_multifunc(self):
        func1 = lambda x,y: x*y
        func2 = lambda x,y: x/y
        funcs = [func1,func2]
        args = [[1,2], [3,4]]
        results = process_parallel_multifunc(funcs, args)
        assert results == [func(*arg) for arg, func in zip(args, funcs)]

    def test_process_parallel_multifunc_timeout(self):
        func1 = lambda x,y: x*y
        func2 = lambda x,y: x/y
        funcs = [func1,func2]
        args = [[1,2], [3,4]]
        results = process_parallel_multifunc(funcs, args, timeout=5)
        assert results == [func(*arg) for arg, func in zip(args, funcs)]
        
    def test_process_parallel_multifunc_one_wrong_func(self):
        func1 = 4
        func2 = lambda x,y: x/y
        funcs = [func1,func2]
        args = [[1,2], [3,4]]
        try:
            process_parallel_multifunc(funcs, args, timeout=5)
        except Exception as e:
            isinstance(e, AssertionError) # check that the error gets caught in assertion

    def test_process_parallel_multifunc_multiple_wrong_func(self):
        func1 = lambda x,y: x*y
        func2 = lambda x,y: x/y
        funcs = [func1,func2]
        args = [[1,2,2], [3,4]]
        try:
            process_parallel_multifunc(funcs, args, timeout=5)
        except Exception as e:
            isinstance(e, AssertionError) # check that the error gets caught in assertion
    def test_process_parallel_multifunc_wrong_args(self):
        func1 = 4
        func2 = "skmc"
        funcs = [func1,func2]
        args = [[1,2], [3,4]]
        try:
            process_parallel_multifunc(funcs, args, timeout=5)
        except Exception as e:
            isinstance(e, AssertionError) # check that the error gets caught in assertionclass TestFirst(unittest.TestCase):


class TestFirst(unittest.TestCase):
    def test_first(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_first(func, args)
        assert results in [func(*arg) for arg in args]

    def test_parallel_timeout(self):
        func = lambda x,y: x*y
        args = [[1,2], [3,4], [5,6], [7,8]]
        results = process_first(func, args, timeout = 5)
        assert results in [func(*arg) for arg in args]
        
    def test_first_wrong_func(self):
        func = None
        args = [[1,2], [3,4], [5,6], [7,8]]
        try:
            process_first(func, args, timeout = 5)
        except Exception as e:
            isinstance(e, AssertionError) # check that the error gets caught in assertionclass TestFirst(unittest.TestCase):

if __name__ == "__main__":
    unittest.main()
from tabnanny import verbose
from typing import Callable
from pydantic import BaseModel
try:
    from process_parallel import *
except:
    from src.process_parallel import *

from typing import Optional

class Parallelizer:
    functions: Optional[list[tuple[Callable, list[list]]]] = []
    
    
    def add_function(self, func: Callable, arguments: list[list]) -> list[list]:
        self.functions.append((func, arguments))
        
    def run(self, n_threads = 5, verbose = False):
        all_funcs = []
        all_args = []
        
        # bring everything into correct format for multifunc processing
        for func, args in self.functions:
            for arg in args:
                all_funcs.append(func)
                all_args.append(arg)
        
        res = process_parallel_multifunc(all_funcs, all_args, n_threads = n_threads, verbose=verbose)
        
        
        results = {}
        i = 0
        for func, args in self.functions:
            results[func.__name__] = []
            for arg in args:
                results[func.__name__].append(res[i])
                i += 1
        
        return results

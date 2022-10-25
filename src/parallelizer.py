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
    
    
    def add_function(self, func: Callable, arguments: list[list] | list[None] | None = None, 
                     kwargs: list[dict] | list[None] | None = None) -> list[list]:
        
        self.functions.append((func, arguments, kwargs))
        
    def run(self, n_threads = 5, verbose = False):
        all_funcs = []
        all_args = []
        all_kwargs = []
        
        # bring everything into correct format for multifunc processing
        for func, args, kwarg in self.functions:
            for arg in args:
                all_funcs.append(func)
                all_args.append(arg)
                all_kwargs.append(kwarg)
                
        res = process_parallel_multifunc(all_funcs, all_args, all_kwargs, n_threads = n_threads, verbose=verbose)
        
        
        results = {}
        i = 0
        for func, args, kwargs in self.functions:
            results[func.__name__] = []
            for arg in args:
                results[func.__name__].append(res[i])
                i += 1
        
        return results

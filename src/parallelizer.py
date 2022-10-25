from typing import Callable
from pydantic import BaseModel
from process_parallel import process_parallel_multifunc
class Parallelizer:
    functions: list[tuple[Callable, list[list]]]
    
    
    def add_function(func: Callable, arguments: list[list]) -> list[list]:
        self.functions.append((func, arguments))
        
    def run():
        all_funcs = []
        all_args = []
        
        # bring everything into correct format for multifunc processing
        for func, args in self.functions:
            for arg in args:
                all_funcs.append(func)
                all_args.append(arg)
        
        return process_parallel_multifunc(all_funcs, all_args)
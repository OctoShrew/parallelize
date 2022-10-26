from ast import Call
import queue
import time
from threading import Lock, Thread
from types import NoneType
from typing import Callable, Dict, Iterable

import numpy as np
from func_timeout import func_timeout

lock = Lock()


def flatten(t):
    """Flatten a list of lists, e.g. [[a,b],[c]] --> [a,b,c] """
    return [
        item for sublist in t if sublist is not None for item in sublist
        if item is not None
    ]


def _process_function(func, idx_args: list, verbose: bool, timeout: int | None, retries: int) -> list | None:
    results = []
    iden = np.random.randint(1000)
    # print(f"Thread {iden} started")
    # as long as we have function calls remaining
    while len(idx_args) > 0:
        with lock:
            idx, argument, kwarg = idx_args.pop(-1)
        try:
            if timeout is None:
                if kwarg is not None:
                    if argument is not None:
                        result = func(*argument, **kwarg)
                    else:
                        result = func(**kwarg)
                else:
                    result = func(*argument)
                    
            else:
                try:
                    if kwarg is not None:
                        if argument is not None:
                            result = func_timeout(timeout, func, args = argument, kwargs=kwarg)
                        else:
                            result = func_timeout(timeout, func, kwargs=kwarg)
                    else:
                        result = func_timeout(timeout, func, args = argument)
                except Exception as e:
                    print(f"The function call for args {argument} has exited with error {e}")
                    raise e
            if verbose:
                print(f"Function call {idx} successful with result {result}")
        except Exception as e: # notify user that call has failed
            result = None 
            print(f"Function call {idx} has failed with error {e}")
        
        
        # if result is not None:
        results.append((idx, result))

    if len(results) >= 1: # return results if there are any
        return results


def process_parallel(func: callable, args: list[list] | list[None] | None = None, kwargs: list[dict] | list[None] | None = None, 
                     timeout: float | None = None, retries: int = 1, n_threads: int = 5, 
                     verbose=False) -> tuple[list[list], list]:
    """ This function created multiple (n_thread) threads and processes them in parallel. It
    takes in a function & a list of args and distributes the function calls (with the respective
    args) across those threads. Especially useful when dealing with e.g. scraping where you might 
    have a limit on the number of threads that can be run in parallel.

    Args:
        func (callable): function that is used for processing
        args (list[list]): list of args that should be passed to the function ([[arg1, arg2], [arg1, arg2], ...])
        retries (int, optional): number of retries for each function. Useful for scraping & other functions that may occasionally fail Defaults to 1.
        n_threads (int, optional): number of threads to use. Defaults to 5.
        verbose (bool, optional): verbosity of the function. true = printout, false = silent. Defaults to False.

    Returns:
        tuple[list[list], list]: _description_
    """
   
    assert isinstance(func, Callable), "Func must be a function"
    assert not isinstance(kwargs, NoneType) or not isinstance(args, NoneType), "At least args or kwargs need to be passed and cannot be None"
    
    if args is not None:
        assert isinstance(args, list), "args must be a list"
        for argument in args:
            assert isinstance(argument, list), "Each passed set of args should be a list"
    else:
        args = [None] * len(kwargs)
        
    if kwargs is not None:
        for kwarg in kwargs:
            assert isinstance(kwarg, Dict)
    else:
        kwargs = [None] * len(args)


    indices = list(
        np.arange(len(args))
    )  # indeces are needed to keep track of which order things should be returned in
    idx_args = [(idx, arg, kwarg) for idx, arg, kwarg in zip(indices, args, kwargs)]
    threads_list = []  # list to store the different threads
    que = queue.Queue()  # queure from which the threads take their data

    # creates desired number of threads
    for _ in range(n_threads):
        threads_list.append(
            Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(
                _process_function(func, idx_args, verbose, timeout, retries)),
                   args=(que, indices, func, args, kwargs)))
        threads_list[-1].start()

    # waits until all data is processed
    time.sleep(1)
    while len(idx_args) > 1:
        time.sleep(0.001) # on some systems (e.g. Mac M1 Pro chips) if no time.sleep is included the while loop slows down
        # the threaded function calls significantly. No idea why but oh well...

    for thread in threads_list:
        thread.join()

    if verbose:
        print("Threads joined")
    results = []

    while not que.empty():
        results.append(que.get())
    print("Results complete")

    results = flatten(results)
    sorted_results = sorted(results, key=lambda tup: tup[0])
    
    return [i[1] for i in sorted_results]


def _process_first_function(func: callable, idx_args: list[tuple], verbose: bool, timeout: float | None):
    global res
    results = []
    while len(idx_args) > 0:
        with lock:
            idx, argument, kwarg = idx_args.pop(-1)
        try:
            if timeout is None:
                if kwarg is not None:
                    if argument is not None:
                        result = func(*argument, **kwarg)
                    else:
                        result = func(**kwarg)
                else:
                    result = func(*argument)
            else:
                try:
                    if kwarg is not None:
                        if argument is not None:
                            result = func_timeout(timeout, func, args = argument, kwargs=kwarg)
                        else:
                            result = func_timeout(timeout, func, kwargs=kwarg)
                    else:
                        result = func_timeout(timeout, func, args = argument)
                except Exception as e:
                    print(f"The function call for args {argument} has exited with error {e}")
                    raise e
            if verbose:
                print(f"Function call {idx} successful.")
        except Exception as e:
            # print(f"Exception: {e}")
            result = None
            print(f"Function call {idx} has failed with exception {e}")
            pass

        # if result is not None:
        results.append((idx, argument, result))
        res.append((idx, argument, result))
    
    if len(results) >= 1:
        # print("Returning results")
        return results

def process_first(func: callable, args: list[list] | None = None, 
                  kwargs: list[dict] | None = None, retries: int = 5, 
                  n_threads: int = 5, verbose: bool = False, timeout: float|None = None):
    """This function creates numtiple (n_thread) threads and waits for the first one that
    returns a result, then returns said result. Currently the other threads will still continue 
    running & complete. 
    
    Good for tasks like pathfinding, where you may want to explore multiple paths at once but
    only choose the first one that was found, rather than waiting for all of them to finish exploration.

    Args:
        func (callable): function that should be executed in the thread
        args (list[list  |  dict]): args to the function that should be executed
        retries (int, optional): number of retries for each function (useful for e.g. scraping). Defaults to 5.
        n_threads (int, optional): number of threads to run. the function calls will automatically be optimally distributed across them. Defaults to 5.
        verbose (bool, optional): verbosity of the function, true = printout, false = silent. Defaults to False.

    Returns:
        _type_: _description_
    """    

    assert isinstance(func, Callable), "Func must be a function"
    assert not isinstance(kwargs, NoneType) or not isinstance(args, NoneType), "At least args or kwargs need to be passed and cannot be None"
    
    if args is not None:
        assert isinstance(args, list), "args must be a list"
        for argument in args:
            assert isinstance(argument, list), "Each passed set of args should be a list"
    else:
        args = [None] * len(kwargs)
        
    
    if kwargs == None:
        kwargs = [None] * len(args)

    
    indices = list(
        np.arange(len(args))
    )  # indices are needed to keep track of which order things should be returned in
    idx_args = [(idx, arg, kwarg) for idx, arg, kwarg in zip(indices, args, kwargs)]
    # print(f"idx args are: {idx_args}")
    threads_list = []  # list to store the different threads
    que = queue.Queue()  # queure from which the threads take their data
    global res
    res = []
    # creates desired number of threads
    for _ in range(n_threads):
        threads_list.append(
            Thread(
                target=lambda q, arg1, arg2, arg3, arg4: q.put(
                    _process_first_function(func, idx_args, verbose, timeout)
                ),
                args=(que, indices, func, args, kwargs),
            )
        )
        threads_list[-1].start()

    # check if there are already results
    while True:
        if len(res) == len(args):
            break
        # print(len(res))
        if len(res) > 0:
            if res[-1][-1] != None:
                break
        time.sleep(0.01) # on some systems (e.g. Mac M1 Pro chips) if no time.sleep is included the while loop slows down
        # the threaded function calls significantly. No idea why but oh well...
    # TODO: Kill the different threads
    return res[-1][2]






def _process_multi_func(idx_args_funcs: list, verbose: bool, timeout: int | None, retries: int) -> list | None:
    results: list = []
    iden = np.random.randint(1000)
    result = None # Added this to avoid result being possibly unset
    
    # as long as we have function calls remaining
    while len(idx_args_funcs) > 0:
        with lock:
            idx, argument, kwarg, func = idx_args_funcs.pop(-1)
        try:
            if timeout is None:
                if kwarg is not None:
                    if argument is not None:
                        result = func(*argument, **kwarg)
                    else:
                        result = func(**kwarg)
                else:
                    result = func(*argument)
            else:
                try:
                    if kwarg is not None:
                        if argument is not None:
                            result = func_timeout(timeout, func, args = argument, kwargs=kwarg)
                        else:
                            result = func_timeout(timeout, func, kwargs=kwarg)
                    else:
                        result = func_timeout(timeout, func, args = argument)
                except Exception as e:
                    print(f"The function call for args {argument} has exited with error {e}")
                    raise e
                    # raise Exception(f"The function call for args {argument} has timed out.")
            if verbose:
                print(f"Function call {idx} successful with result {result}")
        except Exception as e: # notify user that call has failed
            result = None 
            print(f"Function call {idx} has failed with Exception {e}")
        
        
        if result is not None:
            results.append((idx, result))

    if len(results) >= 1: # return results if there are any
        return results


def process_parallel_multifunc(funcs: list[callable], args: list[list], kwargs: list[dict] | list[None] | None = None, 
                               timeout: float | None = None, retries: int = 1, n_threads: int = 5, 
                               verbose=False) -> tuple[list[list], list]:
    """ This function created multiple (n_thread) threads and processes them in parallel. It
    takes in a list of functions & a list of args and distributes the function calls (with the respective
    args) across those threads. Especially useful when dealing with e.g. scraping where you might 
    have a limit on the number of threads that can be run in parallel.

    Args:
        funcs (list[executable]): list of functions used for processing
        args (list[list]): list of args that should be passed to the function ([[arg1, arg2], [arg1, arg2], ...])
        retries (int, optional): number of retries for each function. Useful for scraping & other functions that may occasionally fail Defaults to 1.
        n_threads (int, optional): number of threads to use. Defaults to 5.
        verbose (bool, optional): verbosity of the function. true = printout, false = silent. Defaults to False.

    Returns:
        tuple[list[list], list]: _description_
    """
    assert isinstance(funcs, list), "Funcs must be a list of functions"
    for func in funcs:
        assert isinstance(func, Callable), "Funcs must be a list of functions"
    
    assert not isinstance(kwargs, NoneType) or not isinstance(args, NoneType), "At least args or kwargs need to be passed and cannot be None"
    
    if args is not None:
        assert isinstance(args, list), "args must be a list"
        for argument in args:
            assert isinstance(argument, list), "Each passed set of args should be a list"
    else:
        args = [None] * len(kwargs)
        
    if kwargs is None:
        kwargs = [None] * len(args)

    indices = list(
        np.arange(len(args))
    )  # indeces are needed to keep track of which order things should be returned in
    idx_args_funcs = [(idx, arg, kwarg, func) for idx, arg, kwarg, func in zip(indices, args, kwargs, funcs)]
    threads_list = []  # list to store the different threads
    que = queue.Queue()  # queure from which the threads take their data

    # creates desired number of threads
    for _ in range(n_threads):
        threads_list.append(
            Thread(target=lambda q, arg1, arg2, arg3: q.put(
                _process_multi_func(idx_args_funcs, verbose, timeout, retries)),
                   args=(que, indices, args, kwargs)))
        threads_list[-1].start()

    # waits until all data is processed
    time.sleep(1)
    while len(idx_args_funcs) > 1:
        time.sleep(0.001) # on some systems (e.g. Mac M1 Pro chips) if no time.sleep is included the while loop slows down
        # the threaded function calls significantly. No idea why but oh well...

    for thread in threads_list:
        thread.join()

    if verbose:
        print("Threads joined")
    results = []

    while not que.empty():
        results.append(que.get())
    print("Results complete")

    results = flatten(results)
    sorted_results = sorted(results, key=lambda tup: tup[0])
    
    return [i[1] for i in sorted_results]

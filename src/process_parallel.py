from ast import arguments
from http.server import executable
import numpy as np
import queue
from threading import Thread, Lock
import time
from func_timeout import func_timeout

lock = Lock()


def flatten(t):
    """Flatten a list of lists, e.g. [[a,b],[c]] --> [a,b,c] """
    return [
        item for sublist in t if sublist != None for item in sublist
        if item != None
    ]


def _process_function(func, idx_args: list, verbose: bool, timeout: int | None, retries: int) -> list | None:
    results: list = []
    iden = np.random.randint(1000)
    # print(f"Thread {iden} started")
    # as long as we have function calls remaining
    while len(idx_args) > 0:
        with lock:
            idx, argument = idx_args.pop(-1)
        try:
            if timeout is None:
                result = func(*argument) # get result of function call)
            else:
                try:
                    result = func_timeout(timeout, func, argument)
                except:
                    raise Exception(f"The function call for args {args} has time out.")
            if verbose:
                print(f"Function call {idx} successful with result {result}")
        except: # notify user that call has failed
            result = None 
            print(f"Function call {idx} has failed")
            pass
        
        
        if result is not None:
            results.append((idx, argument, result))

    if len(results) >= 1: # return results if there are any
        return results


def process_parallel(func: executable, arguments: list[list], timeout: float | None = None, 
                     retries: int = 1, n_threads: int = 5, verbose=False) -> tuple[list[list], list]:
    """ This function created multiple (n_thread) threads and processes them in parallel. It
    takes in a function & a list of arguments and distributes the function calls (with the respective
    arguments) across those threads. Especially useful when dealing with e.g. scraping where you might 
    have a limit on the number of threads that can be run in parallel.

    Args:
        func (executable): function that is used for processing
        arguments (list[list]): list of arguments that should be passed to the function ([[arg1, arg2], [arg1, arg2], ...])
        retries (int, optional): number of retries for each function. Useful for scraping & other functions that may occasionally fail Defaults to 1.
        n_threads (int, optional): number of threads to use. Defaults to 5.
        verbose (bool, optional): verbosity of the function. true = printout, false = silent. Defaults to False.

    Returns:
        tuple[list[list], list]: _description_
    """

    indices = list(
        np.arange(len(arguments))
    )  # indeces are needed to keep track of which order things should be returned in
    idx_args = [(idx, arg) for idx, arg in zip(indices, arguments)]
    threads_list = []  # list to store the different threads
    que = queue.Queue()  # queure from which the threads take their data

    # creates desired number of threads
    for _ in range(n_threads):
        threads_list.append(
            Thread(target=lambda q, arg1, arg2, arg3: q.put(
                _process_function(func, idx_args, verbose, timeout, retries)),
                   args=(que, indices, func, arguments)))
        threads_list[-1].start()

    # waits until all data is processed
    time.sleep(1)
    while len(idx_args) > 1:
        time.sleep(0.001) # on some systems (e.g. Mac M1 Pro chips) if no time.sleep is included the while loop slows down
        # the threaded function calls significantly. No idea why but oh well...
        pass

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
    print(sorted_results)
    
    return [i[1] for i in sorted_results], [i[2] for i in sorted_results]

from unittest import result
from func_timeout import func_timeout


def _process_first_function(func: executable, idx_args: list[tuple], verbose: bool, timeout: float | None):
    global res
    results = []
    while len(idx_args) > 0:
        with lock:
            idx, argument = idx_args.pop(-1)
        try:
            if timeout is None:
                result = func(*argument)
            else:
                try:
                    result = func_timeout(timeout, func, args = argument)
                except:
                    raise Exception(f"The function call for args {args} has time out.")
            if verbose:
                print(f"Function call {idx} successful.")
        except:
            # print(f"Exception: {e}")
            result = None
            print(f"Function call {idx} has failed")
            pass

        # if result is not None:
        results.append((idx, argument, result))
        res.append((idx, argument, result))
    if len(results) >= 1:
        # print("Returning results")
        return results

def process_first(func: executable, arguments: list[list | dict], retries: int = 5, 
                  n_threads: int = 5, verbose: bool = False, timeout: float = None):
    """This function creates numtiple (n_thread) threads and waits for the first one that
    returns a result, then returns said result. Currently the other threads will still continue 
    running & complete. 
    
    Good for tasks like pathfinding, where you may want to explore multiple paths at once but
    only choose the first one that was found, rather than waiting for all of them to finish exploration.

    Args:
        func (executable): function that should be executed in the thread
        arguments (list[list  |  dict]): arguments to the function that should be executed
        retries (int, optional): number of retries for each function (useful for e.g. scraping). Defaults to 5.
        n_threads (int, optional): number of threads to run. the function calls will automatically be optimally distributed across them. Defaults to 5.
        verbose (bool, optional): verbosity of the function, true = printout, false = silent. Defaults to False.

    Returns:
        _type_: _description_
    """    
    indices = list(
        np.arange(len(arguments))
    )  # indices are needed to keep track of which order things should be returned in
    idx_args = [(idx, arg) for idx, arg in zip(indices, arguments)]
    # print(f"idx args are: {idx_args}")
    threads_list = []  # list to store the different threads
    que = queue.Queue()  # queure from which the threads take their data
    global res
    res = []
    # creates desired number of threads
    for _ in range(n_threads):
        threads_list.append(
            Thread(
                target=lambda q, arg1, arg2, arg3: q.put(
                    _process_first_function(func, idx_args, verbose, timeout)
                ),
                args=(que, indices, func, arguments),
            )
        )
        threads_list[-1].start()

    # check if there are already results
    while True:
        if len(res) == len(arguments):
            break
        # print(len(res))
        if len(res) > 0:
            if res[-1][-1] != None:
                break
        time.sleep(0.01) # on some systems (e.g. Mac M1 Pro chips) if no time.sleep is included the while loop slows down
        # the threaded function calls significantly. No idea why but oh well...
        pass
    return [res[-1][1]], [res[-1][2]]
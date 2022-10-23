This library was initially created by Felix Quinque (representing OctoShrew Ltd.) and is now released as an open source project. It creates a collection of functions, namely:
- process_parallel: Allows for processing many calls of the same function in parallel
- process_parallel_multifunc: Allows for processing multiple different functions & respective inputs in parallel
- process_first: Processes multiple function calls and continues after first result is found, discards the rest.

You can find examples of their usage in demo.ipynb.


This library is most useful for operations like scraping, where we can send multiple hundred requests at the same time rather than sequentially. Currently, no easy to use way of doing this exists in python to our knowledge. It is planned to add a Pipeline class which allows for building more complex data pipelines with both parallel & sequential processing elements, as well as performance enhancements & the addition to allow for retrying failed function calls (currently exist as a parameter but not yet functionally)


TODO:
- Add retries
- Add kwargs

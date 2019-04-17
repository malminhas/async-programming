# async-programming
Various different ways to do it in Python

## 1. [multiprocessing](https://github.com/malminhas/async-programming/blob/master/multiprocessing.py)
Using multiple processes running on multiple cores to create true *parallelism*.  Each process has a separate memory space.  Requires a larger memory footprint but no sync primitives are needed.  Best for CPU-bound use cases.

## 2. [multithreading](https://github.com/malminhas/async-programming/blob/master/multithreading.py)
Using multiple threads running on the same core to create a sense of *concurrent* operation.  Threads run in the same memory space so has lower memory footprint but is notoriously hard to get right and furthermore CPython suffers from the GIL limitation.  Best for IO-bound use cases.

## 3. [asyncio](https://github.com/malminhas/async-programming/blob/master/multiasyncio.py)
Using *cooperative multitasking* in event loop to provide the feeling of concurrency without incurring the costs.  Builds on Python coroutines.  Best for IO-bound use cases.
From notes [here](https://realpython.com/async-io-python/), the syntax `async def` introduces either a native coroutine or an asynchronous generator.  The expressions `async with` and `async for` are also valid.  A function that you introduce with `async def` is a coroutine.  It may use `await`, `return`, or `yield`, but all of these are optional
The keyword `await` passes function control back to the event loop. It suspends the execution of the surrounding coroutine. 
If Python encounters an `await f()` expression in the scope of `g()`, await tells the event loop, _"Suspend execution of `g()` until whatever I'm waiting on - the result of `f()` - is returned.  In the meantime, go let something else run."_
Using `await` and/or `return` creates a coroutine function. To call a coroutine function, you must await it to get its results.  Note that generator-based coroutine support has been outdated since the async/await syntax was put in place in Python 3.5.

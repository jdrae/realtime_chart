# Milestone 1: Real-time Price Graph

## 1. Get real-time price data from Binance Websocket
- What does 'id' parameter do in binance websocket request?
- Threading
  - Websocket should handle data continuously and in parallel. So, creating another thread is necessary to continue reading while performing other processes
- Logging
  - https://velog.io/@qlgks1/python-python-logging-해부
  - Singleton pattern: Multiple calls to logging.getLogger('someLogger') return a reference to the same logger object as long as it is in the same Python interpreter process.
  - Observer pattern: A change in the state of one object (the Subject) automatically notifies multiple dependent objects (Observers). A single log event is delivered simultaneously to multiple handlers (observers), allowing each handler to process the log independently.
    - All attached handlers are invoked sequentially in the same thread. Internally, threading.RLock is used to prevent race conditions between threads, but this is for thread safety in multi-threaded environments and does not mean that handlers are executed in parallel. Therefore, if there is a slow handler, blocking issues may occur.
  - thread-safe: Uses a reentrant lock to prevent deadlocks and ensure that multiple threads can safely write log messages without corrupting the log output.
    - reentrant lock: It allows the program to continue running normally even if the **same thread** writes log messages recursively or in a nested manner.
    - With a regular lock, this would cause a deadlock because thread-1 would be waiting for itself to release the lock.
  - print() function works synchronously, so when a thread calls print(), it blocks until all the I/O operations are completed.
  - In a multiprocessing program, log messages can become mixed because each process has an independent logging instance.
    - Implement a SocketHandler or QueueHandler to serialize log messages through a single process.
## 2. Send data to Kafka

## 3. Save data from Kafka to Postgresql

## 4. Design Web

## 5. Visualize data from Postgresql to sWeb

## 6. Visualize data from Kafka to Web

## 7. Modify past data in Postgresql (?)
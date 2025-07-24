# Milestone 1: Real-time Price Graph

## 1. Get real-time price data from Binance Websocket
- What does 'id' parameter do in binance websocket request?
  - Maybe, message from server returns faster when using the same id used in initial subscription.
unsubscribe with same id:
```
2025-06-15 19:01:56,460 DEBUG	main.common.websocket.websocket_client 	 Sending message to Binance WebSocket Server: {"method": "UNSUBSCRIBE", "params": ["btcusdt@miniTicker", "ethusdt@miniTicker"], "id": 1749981711272}
2025-06-15 19:01:56,460 INFO	main.binance_connector.data_handler 	 Unsubscribed: ['btcusdt@miniTicker', 'ethusdt@miniTicker']
2025-06-15 19:01:56,460 DEBUG	main.common.websocket.websocket_client 	 Closing websocket
2025-06-15 19:01:56,461 DEBUG	main.common.websocket.websocket_client 	 Websocket closed
{"result":null,"id":1749981711272}
2025-06-15 19:01:56,516 WARNING	main.common.websocket.websocket_client 	 CLOSE frame received, closing websocket connection
2025-06-15 19:01:56,516 INFO	main.binance_connector.data_handler 	 Data handler stopped
```

unsubscribe with different id:
```
2025-06-15 19:00:57,776 DEBUG	main.common.websocket.websocket_client 	 Sending message to Binance WebSocket Server: {"method": "UNSUBSCRIBE", "params": ["btcusdt@miniTicker", "ethusdt@miniTicker"], "id": 1749981657776}
2025-06-15 19:00:57,776 INFO	main.binance_connector.data_handler 	 Unsubscribed: ['btcusdt@miniTicker', 'ethusdt@miniTicker']
2025-06-15 19:00:57,776 DEBUG	main.common.websocket.websocket_client 	 Closing websocket
2025-06-15 19:00:57,777 DEBUG	main.common.websocket.websocket_client 	 Websocket closed
2025-06-15 19:00:57,873 WARNING	main.common.websocket.websocket_client 	 CLOSE frame received, closing websocket connection
2025-06-15 19:00:57,873 INFO	main.binance_connector.data_handler 	 Data handler stopped
{"result":null,"id":1749981657776}
```

- Threading
  - Websocket should handle data continuously and in parallel. So, creating another thread is necessary to continue reading while performing other processes
- Logging
  - Singleton pattern: Multiple calls to logging.getLogger('someLogger') return a reference to the same logger object as long as it is in the same Python interpreter process.
  - Observer pattern: A change in the state of one object (the Subject) automatically notifies multiple dependent objects (Observers). A single log event is delivered simultaneously to multiple handlers (observers), allowing each handler to process the log independently.
    - All attached handlers are invoked sequentially in the same thread. Internally, threading.RLock is used to prevent race conditions between threads, but this is for thread safety in multi-threaded environments and does not mean that handlers are executed in parallel. Therefore, if there is a slow handler, blocking issues may occur.
  - thread-safe: Uses a reentrant lock to prevent deadlocks and ensure that multiple threads can safely write log messages without corrupting the log output.
    - reentrant lock: It allows the program to continue running normally even if the **same thread** writes log messages recursively or in a nested manner.
    - With a regular lock, this would cause a deadlock because thread-1 would be waiting for itself to release the lock.
  - print() function works synchronously, so when a thread calls print(), it blocks until all the I/O operations are completed.
  - In a multiprocessing program, log messages can become mixed because each process has an independent logging instance.
    - Implement a SocketHandler or QueueHandler to serialize log messages through a single process.
- Websocket instance might handle multiple subscriptions. 
  - Check tradeoff between latency and cleancode. 
## 2. Send data to Kafka
- Maybe I can change Kafka to Redis later for instant data access.
- Scope: 1 symbol(BTC) and 1 stream(mini_tikcer) 
  - It can be expanded to multiple symbols and multiple streams. Code should be reusable.
  - How should I define a topic? By symbol or by stream?
    - Considering that I'm developing a personal project, topics should be divided by symbol, since I have no plan of expanding it yet.
    - However, if I have plan to handle multiple symbols, maintaining same data format in one topic should be best practice.
      - So, one websocket client should receive data from the same stream name, but multiple symbols.
      - Different streams might have different data return time, so it'll be clearer to separate each other.
      - But, I can subscribe at most 2 symbols in one stream due to limits. 
- bootstrap_servers only needs to contain a partial list of brokers. 
  - Kafka retrieves cluster information from successfully connected brokers. (list of brokers, partition information, etc.)
  - Scaling a Kafka cluster itself has nothing to do with bootstrap_servers, and Kafka automatically reflects the new brokers in its metadata when scaling.
- async kafka
  - Why? When data is sent synchronously to Kafka, the WebSocket thread is blocked during the sending process. It might occur a bottleneck.
  - How? Asynchronous functions in the kafka class can only be executed in the loop in which that instance is running. Since WebsocketClient runs in its own thread, it calls ayncio.run_coroutine_threadsafe to offload the asynchronous on_message work to another thread.
  - asyncio.sleep
    - Why? The main thread must not terminate so that the event loop stays alive and coroutine tasks can run properly. Threads created with threading.Thread are non-daemon by default, meaning they can stay alive even after the main thread ends. However, in the current code, the thread object is created inside main(), so it disappears when main terminates. 
    - time.sleep? While the main thread is paused and other threads keep running, the event loop in the main thread also stops, making it impossible to register coroutines. As a result, data may be lost.
## 3. Save data from Kafka to Postgresql
- batch insert
- bottleneck -> use thread
## 4. Design Web

## 5. Visualize data from Kafka to Web
- https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio
- memory leak of KafkaConsumer
- dispatcher & async
- overflow
- deque vs queue
  - queue.Queue and collections.deque serve different purposes. queue.Queue is intended for allowing different threads to communicate using queued messages/data, whereas collections.deque is simply intended as a data structure. That's why queue.Queue has methods like put_nowait(), get_nowait(), and join(), whereas collections.deque doesn't. queue.Queue isn't intended to be used as a collection, which is why it lacks the likes of the in operator.
- eventlet, threading, kafka 
- singleton new vs init
## 6. Visualize data from Postgresql to Web
- endpoints for frontend
  - initial
  - periodic
- aggregate raw data batch
  - timing is not a solution. need to use another db
- round milliseconds to prevent overflow
- window calculation from aggregated data
## 7. Modify past data in Postgresql (?)
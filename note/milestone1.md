# Milestone 1: Real-time Price Graph

## 1. Get real-time price data from Binance Websocket
- check binance id
- threading
  - websocket should handle data continuously and in parallel
  - so, creating another thread is necessary to continue reading while performing other processes
- logging
  - singleton pattern: Multi ple calls to logging.getLogger('someLogger') return a reference to the same logger object. This is true not only within the same module, but also across modules as long as it is in the same Python interpreter process.
  - why not print?
## 2. Send data to Kafka

## 3. Save data from Kafka to Postgresql

## 4. Design Web

## 5. Visualize data from Postgresql to sWeb

## 6. Visualize data from Kafka to Web

## 7. Modify past data in Postgresql (?)
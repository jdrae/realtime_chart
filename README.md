# Realtime Crypto Chart

A real-time cryptocurrency price display project built with Django, Flask, and Kafka.

👉 [Check out the demo!](https://jdrae.fyi)

![demo](https://github.com/user-attachments/assets/1c57c08d-5deb-4eb3-af7b-fbf6eb64e622)

## How It Works

1.	Producer: A script connects to Binance’s WebSocket server to receive kline (candlestick) data every second and publishes it to a Kafka topic.
2.	Inserter: Another script consumes the Kafka stream and batches the data for insertion into a PostgreSQL database every minute. During each insertion, it records a checkpoint: the first and last timestamps for each symbol.
3.	Django Celery Task: A scheduled task runs every minute to read the checkpoints and aggregate the 1-second data into 1-minute intervals. This step is technically unnecessary since Binance already provides 1-minute klines, but it was implemented as a personal challenge.
4.	Flask Server: Reads data directly from Kafka and serves it to the frontend via WebSocket every second to display live sidebar prices.

## Example Timeline

To minimize latency, a few heuristic buffer seconds are added throughout the pipeline.

1.	`2m *s`
	* Producer: Binance WebSocket → Kafka Topic
	* Frontend: Kafka Topic → Web Client
2.	`2m 2s`
	* Inserter: Kafka Topic → PostgreSQL kline_1s table
	* Inserts data in the range `[1m 2s, 2m 1s]`
3.	`2m 5s`
	* Django Celery Task: Aggregates data
	* Reads checkpoint table
	* Aggregates 1-second data from `[1m 0s, 1m 59s]` into 1-minute data in aggregated_kline
4.	`2m 7s`
	* Frontend: PostgreSQL aggregated_kline, kline_1s → Frontend
	* Updates the last data point for 1m 0s using aggregated_kline to show volume
	* Adds a new data point for 2m 0s using kline_1s to show the current open price


## Notes
* The frontend UI is designed with a cursor-based vibe.
* All containers (except for the frontend and producer) are deployed on the same instance to reduce costs.
* To save storage and memory, the PostgreSQL container deletes old data every 30 minutes via crontab, and the Kafka topic has a data retention policy of 1 minute.
* The frontend and producer run on the same instance to accurately measure data latency, avoiding discrepancies from server time differences.
* Although a more scalable design would separate Kafka topics and database tables by symbol, the current setup handles just two symbols, with no plans to add more, so they are grouped together.

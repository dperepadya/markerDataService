# Market Data Service

**Market Data Service** is an asynchronous service focused on collecting, processing, and delivering market data from various financial markets. The service uses adapters for different market APIs, which collect data and publish it into a message bus (RabbitMQ queue). The data is then processed and delivered to subscribers or saved for further analysis in a PostgreSQL database (with TimescaleDB support).

![Market Data Service Architecture](images/MDServer.png)

## Features

- **Adapters Library**: The service includes a library of adapters for different financial markets, which collect data based on subscription commands.
- **Data Bus (RabbitMQ)**: Market data is published to a RabbitMQ queue, enabling scalable processing and decoupling of producers and consumers.
- **Async Processing**: The service is fully asynchronous, built on `asyncio` and `aio-pika` for efficient data handling.
- **Market Data Preprocessing**: Data preprocessing features like aggregation and filtering before forwarding to users.
- **ETL Support**: The service can save raw and processed market data into a PostgreSQL database (with TimescaleDB for efficient time-series queries).
- **Web GUI**: An HTML-based FastAPI interface allows users to interact with the service, subscribe to data streams, and view market data.
- **Multiple Databases**: The service supports two PostgreSQL databases: one local and one running inside a Docker container for testing.

## Technologies Used

- **Python**: The primary programming language.
- **FastAPI**: Web framework for the API and GUI.
- **aio-pika**: Asynchronous library for interacting with RabbitMQ.
- **asyncio**: Python's core library for writing asynchronous programs.
- **PostgreSQL**: The primary database used for storing market data, with optional TimescaleDB for time-series optimizations.
- **TimescaleDB**: An extension of PostgreSQL that allows fast queries for time-series data.
- **RabbitMQ**: Message broker used for managing the data pipeline.
- **Docker**: Used to containerize the services for easier deployment and testing.

## Running the Application with Docker Compose

The project includes a `docker-compose.yml` file for running the application, RabbitMQ and PostgreSQL database.

**Build and Start Containers:**
   ```bash
   docker-compose up --build
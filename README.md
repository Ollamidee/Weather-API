# Weather API

A simple Flask-based Weather API that fetches data from Visual Crossing, incorporates Redis for caching, and includes rate limiting using Flask-Limiter. It reads its configuration (API keys, Redis connection details) directly from system environment variables.

## Features
* Fetches current and forecast weather data.
* Caches API responses in Redis for faster subsequent requests and reduced external API calls.
* Implements rate limiting to control user access and protect external API usage.
* Provides clear error handling for API failures and rate limits.

## Technologies Used
* **Flask:** Web framework
* **Flask-Limiter:** For rate limiting
* **Requests:** For making HTTP requests to external APIs
* **Redis:** In-memory data structure store (used for caching)


## Project Information

[Project Source](https://roadmap.sh/projects/weather-api-wrapper-service)
[Project Page](https://github.com/Ollamidee/Weather-API)

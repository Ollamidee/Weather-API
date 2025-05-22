import os
import json
import redis
import requests
from datetime import timedelta
from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per day", "2 per hour"],
)



#Retrieving the redis string and visual crossing api from the environment variable
redis_host = os.environ.get("REDIS_HOST")
redis_port = int(os.environ.get("REDIS_PORT"))
redis_db = int(os.environ.get("REDIS_DB"))
my_api_key = os.environ.get("VISUAL_CROSSING_API")


redis_connection = redis.Redis(host=redis_host, port=redis_port, db=redis_db)




print("test 1")






def weather_data(city, country):
    print("test 2")
    if redis_connection: # Only try to get from Redis if connection was successful
        weather_report_json = redis_connection.get(f"{city}, {country}")
        if weather_report_json:
            print("Weather data found in Redis cache.")
            return json.loads(weather_report_json) # Return plain Python dict

    # If not in cache or Redis not connected, fetch from Visual Crossing
    print("Fetching weather data from Visual Crossing API.")
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city},{country}?key={my_api_key}&contentType=json"

    try:
        weth = requests.get(url)
        weth.raise_for_status() # Raise an exception for HTTP errors

        weather_info = weth.json() # Get the JSON response as a Python dict

        # Cache in Redis if connection is available
        if redis_connection:
            print("Caching weather data in Redis.")
            redis_connection.setex(f"{city}, {country}", timedelta(hours=12), json.dumps(weather_info))

        return weather_info # Return the fetched data as a plain Python dict

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {weth.text if weth else 'No response text'}")
        # Return a dictionary for errors
        if weth and weth.status_code == 429:
            return {"error": "Take a break, you've sent too many requests to the external API.", "status_code": 429}
        else:
            return {"error": f"External API request failed: {http_err}", "status_code": weth.status_code if weth else 500}
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        return {"error": "Could not connect to external weather service.", "status_code": 503}
    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error: {json_err} - Raw response: {weth.text if weth else 'No response text'}")
        return {"error": "Received invalid JSON from external weather service.", "status_code": 500}



@app.route('/timeline/<city>/<country>')
@limiter.limit("3 per hour")
def weather_request(city, country):
    print("test 3")
    # Get the data from weather_data
    weather_data_result = weather_data(city, country)

    if isinstance(weather_data_result, dict) and "error" in weather_data_result:
        # If weather_data returned an error, return it with the appropriate status code
        status_code = weather_data_result.get("status_code", 500)
        return jsonify({"message": weather_data_result["error"]}), status_code
    elif weather_data_result:
        # Successfully retrieved weather data, now format it for your API's response
        return jsonify(weather_data_result), 200 # Return the full dict as JSON with 200 OK
    else:
        # Fallback for unexpected cases where weather_data returned None without an error dict
        return jsonify({"message": "An unexpected error occurred while fetching weather data."}), 500


if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
import sys
import requests
import matplotlib.pyplot as plt
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import datetime as dt
import meteomatics.api as api
import json
import pandas as pd

def get_weather_data(api_key, latitude, longitude, timestamp):
    units = 'metric'
    lang = 'en'

    url = f'http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&appid={api_key}&units={units}&lang={lang}&dt={int(timestamp)}'

    response = requests.get(url)
    data = response.json()

    # Check if the response contains 'current' key
    if 'current' in data:
        # Extract relevant information from the API response
        weather_info = {
            'date': timestamp,
            'temperature': data['current']['temp'],
            'feels_like': data['current']['feels_like'],
            'description': data['current']['weather'][0]['description'],
            'humidity': data['current']['humidity'],
            'wind_speed': data['current']['wind_speed'],
            'wind_gust': data['current']['wind_gust'],
            'wind_deg': data['current']['wind_deg'],
            'dew_point': data['current']['dew_point'],
            'pressure': data['current']['pressure'],
            'humidity': data['current']['humidity'],
            'clouds': data['current']['clouds'],        
        }

        return weather_info
    else:
        raise ValueError(f"Unable to extract weather information. OpenWeatherMap API response: {data}")

# New Credentials: valid till 2023-12-21
username = 'isro_university_columbia'
password = 'CSx172fQer'

# Retrieve the selected date from command-line arguments
selected_date_str = sys.argv[1]
selected_date = dt.datetime.strptime(selected_date_str, "%Y-%m-%d")

# Set the time range
end_date = selected_date + dt.timedelta(days=1)
interval = dt.timedelta(hours=1)

# Create a more granular grid for northwest France with 0.1-degree increment
latitude_range = np.arange(47, 51.1, 0.25)
longitude_range = np.arange(-7, 2.1, 0.25)

# Parameters to retrieve
parameters = ['t_2m:C', 'precip_1h:mm', 'wind_speed_10m:ms']

# Model to use
model = 'mix'

# Query Meteomatics API for time series data
df = api.query_time_series([(latitude, longitude) for latitude in latitude_range for longitude in longitude_range],
                           selected_date, end_date, interval, parameters, username, password, model=model)

# Create the folder path if it doesn't exist
folder_path = os.path.join('static', 'predictions')
os.makedirs(folder_path, exist_ok=True)

# Add latitude, longitude, and timestamp columns
df['latitude'] = np.repeat(latitude_range, len(longitude_range) * len(pd.date_range(selected_date, end_date, freq=interval)))
df['longitude'] = np.tile(np.repeat(longitude_range, len(latitude_range)), len(pd.date_range(selected_date, end_date, freq=interval)))
df['timestamp'] = np.tile(pd.date_range(selected_date, end_date, freq=interval), len(latitude_range) * len(longitude_range))

# Save the DataFrame to a JSON file in the specified folder
result_json = df.to_json(orient='records', lines=True)
file_path = os.path.join(folder_path, f'model-pred_{selected_date_str}.txt')
with open(file_path, 'w') as file:
    file.write(result_json)

# # Convert DataFrame to JSON and write to file
# result_json = df.to_json(orient='records', lines=True)
# with open('static/predictions/model-pred.txt', 'w') as file:
#     file.write(result_json)

# # Save openweather data to a text file
# with open("static/predictions/model-pred.txt", "w") as file:
#     file.write(str(df))

# Extracting data from the DataFrame
timestamps = df.index
temperature_data = df['t_2m:C'].rolling(window=3, min_periods=1).mean().values
precipitation_data = df['precip_1h:mm'].rolling(window=3, min_periods=1).mean().values
wind_speed_data = df['wind_speed_10m:ms'].rolling(window=3, min_periods=1).mean().values

# Extracting latitude and longitude from the index
latitudes = [index[0] for index in df.index]
longitudes = [index[1] for index in df.index]

# Plotting with Cartopy projections and common map features
os.makedirs("static/predictions", exist_ok=True)

# Plot temperature
fig, ax = plt.subplots(figsize=(10, 7), subplot_kw={'projection': ccrs.PlateCarree()})
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, edgecolor='black')
ax.add_feature(cfeature.LAKES, edgecolor='black')
sc1 = ax.scatter(longitudes, latitudes, c=temperature_data, cmap='coolwarm', s=200, transform=ccrs.PlateCarree())
ax.set_title('Temperature (°C)')
plt.colorbar(sc1, ax=ax, label='Temperature (°C)')
plt.savefig(os.path.join("static/predictions", "temperature_plot.png"))
plt.clf()

# Plot precipitation
fig, ax = plt.subplots(figsize=(10, 7), subplot_kw={'projection': ccrs.PlateCarree()})
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, edgecolor='black')
ax.add_feature(cfeature.LAKES, edgecolor='black')
sc2 = ax.scatter(longitudes, latitudes, c=precipitation_data, cmap='Blues', s=200, transform=ccrs.PlateCarree())
ax.set_title('Precipitation (mm)')
plt.colorbar(sc2, ax=ax, label='Precipitation (mm)')
plt.savefig(os.path.join("static/predictions", "precipitation_plot.png"))
plt.clf()

# Plot wind speed
fig, ax = plt.subplots(figsize=(10, 7), subplot_kw={'projection': ccrs.PlateCarree()})
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, edgecolor='black')
ax.add_feature(cfeature.LAKES, edgecolor='black')
sc3 = ax.scatter(longitudes, latitudes, c=wind_speed_data, cmap='viridis', s=200, transform=ccrs.PlateCarree())
ax.set_title('Wind Speed (m/s)')
plt.colorbar(sc3, ax=ax, label='Wind Speed (m/s)')
plt.savefig(os.path.join("static/predictions", "wind_speed_plot.png"))
plt.clf()

# Fetch openweather API data and save it to a text file
api_key = '30b11b3640b39d0cadcb19e2689709e7'

# Convert the selected date to a Unix timestamp
timestamp = selected_date.timestamp()

# Fetch openweather API data
openweather_data = get_weather_data(api_key, latitudes[0], longitudes[0], timestamp)

# Save openweather data to a text file
with open("static/predictions/weather-pred.txt", "w") as file:
    json.dump(openweather_data, file)
    
# openweather_data = get_weather_data(api_key, latitudes[0], longitudes[0], selected_date.timestamp())

# with open("static/predictions/weather-pred.txt", "w") as file:
#     file.write(str(openweather_data))

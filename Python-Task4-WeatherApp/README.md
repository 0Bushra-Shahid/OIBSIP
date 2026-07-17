# Weather App (Advanced) — Python Programming Track

## Objective
A Python desktop application that fetches and displays real-time weather data
for a user-specified city, including current conditions and a 5-day forecast,
using the OpenWeatherMap API.

## Tech Stack
- Python 3
- `tkinter` — GUI
- `requests` — API calls
- `Pillow (PIL)` — loading weather icon images

## Features
- City input field with a "Get Weather" button (Enter key also works)
- Displays: temperature, "feels like" temperature, today's actual low/high
  range, condition, humidity, wind speed, and a weather icon
- 5-day forecast shown as mini cards, each with date, icon, and a
  min/max temperature range for that day
- Celsius / Fahrenheit toggle button
- Soft blue gradient background with all content inside a floating card
- Resizable window with a working maximize/restore button
- Error handling for: empty input, city not found, network timeout,
  connection errors

## Setup Instructions
1. Install dependencies:
   ```
   pip install requests pillow
   ```
2. Get a free API key from [openweathermap.org](https://openweathermap.org/api)
   (Sign up → API keys tab → copy the "Default" key)
3. Make a copy of `config_example.py` and rename it to `config.py`.
   Open `config.py` and replace:
   ```python
   API_KEY = "PASTE_YOUR_OPENWEATHERMAP_API_KEY_HERE"
   ```
   with your actual key.
   (`config.py` is listed in `.gitignore` so your personal key is never
   pushed to GitHub.)
4. Run the app:
   ```
   python weather_app_advanced.py
   ```

## Project Files
| File | Purpose |
|---|---|
| `weather_app_advanced.py` | Main application code |
| `config_example.py` | Template showing where to put your API key |
| `config.py` | Your personal API key (create this yourself — not included in the repo) |
| `.gitignore` | Prevents `config.py` from being uploaded to GitHub |

## Technical Notes

### Why does temperature sometimes differ slightly from other weather apps?
Different weather providers (OpenWeatherMap, Google Weather, AccuWeather, etc.)
use different data sources and forecast models. A difference of a few degrees
between apps is normal and expected, especially during extreme weather
conditions such as heatwaves.

### Timezone handling
OpenWeatherMap's forecast API returns timestamps in UTC. Since this matters
for correctly grouping data into "today", "tomorrow", etc. for cities in
different timezones (e.g. Pakistan is UTC+5), this app converts every
timestamp to the target city's local time (using the `timezone` offset
provided in the API response) before grouping forecast entries by date.
This ensures the daily min/max ranges reflect the correct local day.

### Why isn't "Range Today" the same as the current temperature?
The current-weather endpoint's `temp_min`/`temp_max` fields do not represent
a full day's range — they are often equal to the current temperature. To show
a meaningful "today's low/high", this app instead scans the 5-day forecast
API's 3-hourly entries for the current local date and computes the actual
minimum and maximum from those.

### API key activation delay
A newly generated OpenWeatherMap API key can take 10 minutes to 2 hours
to activate. If you see an "Invalid API key" error immediately after
signing up, wait and try again.

### Internet requirement
Weather icons are fetched live from OpenWeatherMap's icon server, so an
internet connection is required to see them.

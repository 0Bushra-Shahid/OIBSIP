"""
Advanced Weather App
---------------------
Features:
- GUI built with Tkinter
- Fetches current weather + 5-day forecast from OpenWeatherMap API
- Displays weather icons
- Celsius / Fahrenheit toggle
- Graceful error handling (city not found, network issues, empty input)
"""

import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
from config import API_KEY   # API key is now stored separately (see config.py)

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "https://openweathermap.org/img/wn/{icon_code}@2x.png"

# Global variable to remember which unit is currently selected
current_unit = "metric"   # "metric" = Celsius, "imperial" = Fahrenheit

# Store the last fetched raw data so we can re-display it when toggling units
last_weather_data = None
last_forecast_data = None


# -------------------------------------------------------------------
# COLOR THEME - Deep Blue & White (with a soft gradient "sky" background)
# -------------------------------------------------------------------
GRADIENT_TOP = "#0B3D66"      # Deep blue at the top of the window
GRADIENT_BOTTOM = "#3A7CA8"   # Softer, lighter blue near the bottom - gives a subtle "sky" feel
CARD_BLUE = "#0F4A78"         # Background for the floating content card
FORECAST_CARD_BLUE = "#1A5C8F"  # Slightly lighter blue for each forecast mini-card
ACCENT_BLUE = "#2E8BC0"       # Buttons
WHITE = "#FFFFFF"             # Text and entry background


def hex_to_rgb(hex_color):
    """Converts a color like '#0B3D66' into an (R, G, B) tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Converts an (R, G, B) tuple back into a color string like '#0B3D66'."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def draw_gradient(canvas, width, height, top_color, bottom_color):
    """
    Draws a smooth vertical gradient on the given canvas by painting many
    thin horizontal lines, each one blended slightly further from the top
    color towards the bottom color. This gives the window a soft,
    weather/sky-like backdrop instead of one flat color.
    """
    canvas.delete("gradient")   # Clear any previous gradient before redrawing
    top_rgb = hex_to_rgb(top_color)
    bottom_rgb = hex_to_rgb(bottom_color)

    for y in range(height):
        # 'ratio' goes from 0.0 (top) to 1.0 (bottom)
        ratio = y / max(height, 1)
        blended_rgb = tuple(
            int(top_rgb[i] + (bottom_rgb[i] - top_rgb[i]) * ratio)
            for i in range(3)
        )
        canvas.create_line(0, y, width, y, fill=rgb_to_hex(blended_rgb), tags="gradient")


# -------------------------------------------------------------------
# MAIN WINDOW SETUP
# -------------------------------------------------------------------
root = tk.Tk()
root.title("Weather App")
root.geometry("450x650")
root.resizable(True, True)   # Allows the maximize/restore-down button to work
root.configure(bg=GRADIENT_TOP)

# Canvas fills the whole window and holds the gradient background
background_canvas = tk.Canvas(root, highlightthickness=0)
background_canvas.pack(fill="both", expand=True)

# All the app's content lives inside this floating "card" frame, which sits
# on top of the gradient canvas - this is what gives the soft-background look.
main_frame = tk.Frame(background_canvas, bg=CARD_BLUE, padx=15, pady=5)
card_window_id = background_canvas.create_window(225, 30, anchor="n", window=main_frame)

# Draw the initial gradient once the window has a real size, and keep the
# card horizontally centered no matter how the window is resized/maximized
def on_canvas_resize(event):
    draw_gradient(background_canvas, event.width, event.height, GRADIENT_TOP, GRADIENT_BOTTOM)
    background_canvas.coords(card_window_id, event.width / 2, 30)   # Re-center the card

background_canvas.bind("<Configure>", on_canvas_resize)

# -------------------------------------------------------------------
# TOP SECTION: City input + search button
# -------------------------------------------------------------------
top_frame = tk.Frame(main_frame, bg=CARD_BLUE)
top_frame.pack(pady=15)

city_label = tk.Label(top_frame, text="Enter City Name:", font=("Arial", 12), bg=CARD_BLUE, fg=WHITE)
city_label.grid(row=0, column=0, padx=5)

city_entry = tk.Entry(top_frame, font=("Arial", 12), width=18, bg=WHITE, fg=CARD_BLUE,
                       insertbackground=CARD_BLUE)   # insertbackground = cursor color
city_entry.grid(row=0, column=1, padx=5)

search_button = tk.Button(top_frame, text="Get Weather", font=("Arial", 11, "bold"),
                           bg=ACCENT_BLUE, fg=WHITE, activebackground=FORECAST_CARD_BLUE,
                           activeforeground=WHITE, relief="flat", padx=8)
search_button.grid(row=0, column=2, padx=5)

# -------------------------------------------------------------------
# UNIT TOGGLE BUTTON (Celsius / Fahrenheit)
# -------------------------------------------------------------------
unit_button = tk.Button(main_frame, text="Switch to \u00b0F", font=("Arial", 10, "bold"),
                         bg=ACCENT_BLUE, fg=WHITE, activebackground=FORECAST_CARD_BLUE,
                         activeforeground=WHITE, relief="flat", padx=6)
unit_button.pack(pady=(0, 10))

# -------------------------------------------------------------------
# CURRENT WEATHER DISPLAY SECTION
# -------------------------------------------------------------------
weather_icon_label = tk.Label(main_frame, bg=CARD_BLUE)
weather_icon_label.pack()

result_label = tk.Label(main_frame, text="", font=("Arial", 12), justify="left", bg=CARD_BLUE, fg=WHITE)
result_label.pack(pady=10)

# -------------------------------------------------------------------
# FORECAST SECTION (5-day forecast shown as a row of mini-cards)
# -------------------------------------------------------------------
forecast_frame = tk.Frame(main_frame, bg=CARD_BLUE)
forecast_frame.pack(pady=20)

# We will create 5 empty "cards" now and fill them later with data
forecast_cards = []
for i in range(5):
    card = tk.Frame(forecast_frame, borderwidth=0, bg=FORECAST_CARD_BLUE, padx=5, pady=5)
    card.grid(row=0, column=i, padx=3)

    day_label = tk.Label(card, text="", font=("Arial", 9, "bold"), bg=FORECAST_CARD_BLUE, fg=WHITE)
    day_label.pack()

    icon_label = tk.Label(card, bg=FORECAST_CARD_BLUE)
    icon_label.pack()

    temp_label = tk.Label(card, text="", font=("Arial", 9), bg=FORECAST_CARD_BLUE, fg=WHITE)
    temp_label.pack()

    # Save references so we can update these labels later
    forecast_cards.append({
        "frame": card,
        "day": day_label,
        "icon": icon_label,
        "temp": temp_label,
        "icon_image": None   # Will hold the image reference (needed to prevent garbage collection)
    })


# -------------------------------------------------------------------
# HELPER FUNCTION: Download and load a weather icon from a URL
# -------------------------------------------------------------------
def load_icon(icon_code, size=(60, 60)):
    """
    Downloads a weather icon image from OpenWeatherMap and returns
    a Tkinter-compatible image object.
    """
    try:
        url = ICON_URL.format(icon_code=icon_code)
        response = requests.get(url, timeout=5)
        image_data = Image.open(io.BytesIO(response.content))
        image_data = image_data.resize(size)
        return ImageTk.PhotoImage(image_data)
    except Exception:
        # If icon fails to load, just return None (app should not crash)
        return None


# -------------------------------------------------------------------
# HELPER FUNCTION: Return the correct temperature symbol for current unit
# -------------------------------------------------------------------
def unit_symbol():
    return "\u00b0C" if current_unit == "metric" else "\u00b0F"


# -------------------------------------------------------------------
# MAIN FUNCTION: Fetch current weather + forecast, then display it
# -------------------------------------------------------------------
def get_weather():
    global last_weather_data, last_forecast_data

    city = city_entry.get().strip()

    # Validate input: reject empty city name
    if city == "":
        messagebox.showerror("Input Error", "Please enter a city name.")
        return

    try:
        # ---- Fetch CURRENT weather ----
        current_params = {"q": city, "appid": API_KEY, "units": current_unit}
        current_response = requests.get(BASE_URL, params=current_params, timeout=5)
        current_data = current_response.json()

        # Check if the city was found (OpenWeatherMap returns cod=404 if not)
        if str(current_data.get("cod")) != "200":
            messagebox.showerror("City Not Found", f"Could not find weather data for '{city}'.")
            return

        # ---- Fetch 5-DAY FORECAST ----
        forecast_params = {"q": city, "appid": API_KEY, "units": current_unit}
        forecast_response = requests.get(FORECAST_URL, params=forecast_params, timeout=5)
        forecast_data = forecast_response.json()

        # Save the raw data globally so the unit toggle can reuse it
        last_weather_data = current_data
        last_forecast_data = forecast_data

        # Compute today's real low/high using the forecast data (more accurate
        # than the current-weather endpoint's temp_min/temp_max fields)
        today_min, today_max = get_today_range_from_forecast(forecast_data)

        display_current_weather(current_data, today_min, today_max)
        display_forecast(forecast_data)

    except requests.exceptions.Timeout:
        messagebox.showerror("Network Error", "The request timed out. Please check your internet connection.")
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Network Error", "Could not connect. Please check your internet connection.")
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"Something went wrong: {e}")


# -------------------------------------------------------------------
# DISPLAY FUNCTION: Show current weather details + icon
# -------------------------------------------------------------------
def get_today_range_from_forecast(forecast_data):
    """
    The 'current weather' endpoint's temp_min/temp_max fields do NOT represent
    a full day's range - they often just equal the current temperature.
    To get a real "today's low/high", we scan the forecast API's 3-hourly
    entries for today's date (in LOCAL time, not UTC) and find the actual
    minimum and maximum.
    """
    from datetime import datetime, timedelta

    # The API's dt_txt values are in UTC. We must shift them by the city's
    # timezone offset (in seconds) to know what LOCAL date/time they represent.
    tz_offset_seconds = forecast_data["city"]["timezone"]

    def to_local_date(entry):
        utc_time = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
        local_time = utc_time + timedelta(seconds=tz_offset_seconds)
        return local_time.strftime("%Y-%m-%d")

    # Determine "today" in the CITY's local time, not the user's own device time
    city_now = datetime.utcnow() + timedelta(seconds=tz_offset_seconds)
    today_str = city_now.strftime("%Y-%m-%d")

    todays_entries = [
        entry for entry in forecast_data["list"]
        if to_local_date(entry) == today_str
    ]

    if not todays_entries:
        # If no entries match today (e.g. it's already late in the day),
        # fall back to the very first available local date in the forecast list.
        first_date = to_local_date(forecast_data["list"][0])
        todays_entries = [
            entry for entry in forecast_data["list"]
            if to_local_date(entry) == first_date
        ]

    temp_min = min(entry["main"]["temp_min"] for entry in todays_entries)
    temp_max = max(entry["main"]["temp_max"] for entry in todays_entries)
    return temp_min, temp_max


def display_current_weather(data, today_min, today_max):
    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]   # Perceived temperature (accounts for humidity/wind)
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"].title()
    wind_speed = data["wind"]["speed"]
    icon_code = data["weather"][0]["icon"]
    city_name = data["name"]
    country = data["sys"]["country"]   # Country code, helps confirm the correct city was matched

    result_text = (
        f"City: {city_name}, {country}\n"
        f"Temperature: {temperature}{unit_symbol()}  (Feels like: {feels_like}{unit_symbol()})\n"
        f"Range Today: {round(today_min)}{unit_symbol()} / {round(today_max)}{unit_symbol()}\n"
        f"Condition: {description}\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind_speed} {'m/s' if current_unit == 'metric' else 'mph'}"
    )
    result_label.config(text=result_text)

    # Load and display the main weather icon
    icon_image = load_icon(icon_code, size=(80, 80))
    if icon_image:
        weather_icon_label.config(image=icon_image)
        weather_icon_label.image = icon_image   # Keep a reference (prevents image from disappearing)


# -------------------------------------------------------------------
# DISPLAY FUNCTION: Show 5-day forecast in the mini-cards
# -------------------------------------------------------------------
def display_forecast(data):
    """
    The forecast API returns data every 3 hours for 5 days (40 entries total),
    with timestamps in UTC. We convert each entry to the city's LOCAL date
    before grouping, so that "today", "tomorrow", etc. line up correctly with
    what a person in that city would actually experience.
    For each local day, we find the lowest and highest temperature across
    all its 3-hour entries - just like a typical mobile weather app.
    """
    from datetime import datetime, timedelta

    tz_offset_seconds = data["city"]["timezone"]

    def to_local_date(entry):
        utc_time = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
        local_time = utc_time + timedelta(seconds=tz_offset_seconds)
        return local_time.strftime("%Y-%m-%d")

    # Group all entries by their LOCAL date, e.g. {"2026-07-16": [entry1, ...], ...}
    entries_by_date = {}

    for entry in data["list"]:
        local_date = to_local_date(entry)
        if local_date not in entries_by_date:
            entries_by_date[local_date] = []
        entries_by_date[local_date].append(entry)

    # Sort dates so they appear in chronological order
    sorted_dates = sorted(entries_by_date.keys())

    # Fill each of the 5 cards with data
    for i, card in enumerate(forecast_cards):
        if i < len(sorted_dates):
            date_part = sorted_dates[i]
            day_entries = entries_by_date[date_part]

            # Find the min and max temperature across all entries for that local day
            temp_min = min(entry["main"]["temp_min"] for entry in day_entries)
            temp_max = max(entry["main"]["temp_max"] for entry in day_entries)

            # Use the midday entry's icon if available, otherwise the first entry
            midday_entry = day_entries[len(day_entries) // 2]
            icon_code = midday_entry["weather"][0]["icon"]

            # Show just the month-day part (e.g., "07-16")
            short_date = date_part[5:]

            card["day"].config(text=short_date)
            card["temp"].config(text=f"{round(temp_min)}\u00b0/{round(temp_max)}\u00b0")

            icon_image = load_icon(icon_code, size=(40, 40))
            if icon_image:
                card["icon"].config(image=icon_image)
                card["icon"].image = icon_image
                card["icon_image"] = icon_image
        else:
            # Not enough data - clear the card
            card["day"].config(text="")
            card["temp"].config(text="")
            card["icon"].config(image="")


# -------------------------------------------------------------------
# UNIT TOGGLE FUNCTION: Switch between Celsius and Fahrenheit
# -------------------------------------------------------------------
def toggle_unit():
    global current_unit

    if current_unit == "metric":
        current_unit = "imperial"
        unit_button.config(text="Switch to \u00b0C")
    else:
        current_unit = "metric"
        unit_button.config(text="Switch to \u00b0F")

    # Re-fetch weather in the new unit if a city has already been searched
    if last_weather_data is not None:
        get_weather()


# -------------------------------------------------------------------
# CONNECT BUTTONS TO THEIR FUNCTIONS
# -------------------------------------------------------------------
search_button.config(command=get_weather)
unit_button.config(command=toggle_unit)

# Allow pressing "Enter" key in the entry box to trigger search
city_entry.bind("<Return>", lambda event: get_weather())

# -------------------------------------------------------------------
# START THE APPLICATION
# -------------------------------------------------------------------
root.mainloop()
import os
import folium
from folium import plugins
import pysolar.solar as solar
from datetime import datetime
from pytz import timezone, exceptions
import time
import webview
import threading
import math

from team_member import load_team_members
from config import load_base_radius, load_map_height, load_team_name

#Get the directory where the script is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the file path for config.json
config_path = os.path.join(current_directory, 'config', 'config.json')

# Construct the file path for the icon image
icon_path = os.path.join(current_directory, 'resources', 'person_icon.png')

# Construct the map path for the map.html
map_path = os.path.join(current_directory, 'resources', 'map.html')

# Function to get current time in a specific timezone
def get_current_time(tz):
    try:
        now = datetime.now(timezone(tz))
        return now.strftime("%H:%M")
    except (exceptions.UnknownTimeZoneError, AttributeError):
        print(f"Error: Invalid timezone '{tz}'")
        return "Unknown"

# Function to check if within working hours
def is_within_working_hours(tz, working_hours):
    try:
        now = datetime.now(timezone(tz))
        start, end = map(int, working_hours.split('-'))
        current_hour = now.hour
        return start <= current_hour < end
    except (exceptions.UnknownTimeZoneError, AttributeError):
        print(f"Error: Invalid timezone '{tz}'")
        return False

# Function to calculate the adjusted radius
def get_adjusted_radius(lat, base_radius):
    try:
        # Scale the radius by the cosine of the latitude
        scale_factor = math.cos(math.radians(float(lat)))
        adjusted_radius = base_radius * scale_factor
        return adjusted_radius
    except (ValueError, TypeError):
        print(f"Error: Invalid latitude value '{lat}'")
        return base_radius  # Return unadjusted radius as fallback

# Function to update the map
def update_map(team_members):
    m = folium.Map(location=[20, 0],
                   zoom_start=2,
                   zoom_control=False,
                   scrollWheelZoom=False,
                   dragging=False)
    folium.plugins.Terminator().add_to(m)
    bounds = []
    for member in team_members:
        coords = member.coordinates.split(',')
        lat, lon = map(float, coords)
        bounds.append([lat, lon])

        # Get current time
        current_time = get_current_time(member.timezone)

        # Check if within working hours
        within_working_hours = is_within_working_hours(member.timezone, member.working_hours)

        # Create a marker with a circular avatar
        if within_working_hours:
            icon_color = 'green'
        else:
            icon_color = 'red'
        
        icon = folium.features.CustomIcon(icon_path, icon_size=(20, 20))
        marker = folium.Marker(
            location=coords,
            icon=icon,
            tooltip=f"<b>{member.name or 'Unknown'}</b><br> Current Time: {current_time or 'N/A'}<br />Working hours: {member.working_hours or 'N/A'}"
        )
        marker.add_to(m)

        # Calculate the adjusted radius
        base_radius = load_base_radius(config_path)  # Load the base radius from the config
        adjusted_radius = get_adjusted_radius(lat, base_radius) # Adjust the radius based on the Mercator projection

        # Add a circle around the marker with the adjusted radius
        folium.Circle(location=coords, radius=adjusted_radius, color=icon_color, fill=True, fill_opacity=0.2).add_to(m)
    
    # Fit the map to the bounds of all team members
    m.fit_bounds(bounds)

    # Save the map to an HTML file
    m.save(map_path)

def refresh_map_loop(window, event, last_updated, team_members):
    while event.is_set():
        if time.time() - last_updated >= 120:
            print("Refreshing map...")
            update_map(team_members)
            window.load_url(f'file://{map_path}')
            last_updated = time.time()
        time.sleep(0.1)


def main():
    # Load the team members
    team_members = load_team_members(config_path)

    update_map(team_members)  # initial map generation
    
    # Get configured map height
    map_height = load_map_height(config_path)

    # Get configured team name
    team_name = load_team_name(config_path)

    # Start the pywebview window
    window = webview.create_window(team_name, f'file://{map_path}',width=2*map_height, height=map_height, resizable=False)

    ## this handles stopping the watcher
    thread_running = threading.Event()
    thread_running.set()

    # Start the background thread to regenerate HTML
    reload_thread=threading.Thread(target=refresh_map_loop, args=(window,thread_running, time.time(),team_members))
    reload_thread.start()

    webview.start()

    ## upon the webview app exiting, stop the watcher
    thread_running.clear()
    reload_thread.join()

    # Delete the HTML file stored in map_path
    try:
        os.remove(map_path)
    except FileNotFoundError:
        print("Map file not found, nothing to delete.")
    except Exception as e:
        print(f"Error while deleting the map file: {e}")

if __name__ == '__main__':
    main()
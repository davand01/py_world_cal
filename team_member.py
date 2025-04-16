import json
import os

class TeamMember:
    def __init__(self, name, timezone, coordinates, working_hours):
        self.name = name
        self.timezone = timezone
        self.coordinates = coordinates
        self.working_hours = working_hours

    def __repr__(self):
        return f"TeamMember(name={self.name}, timezone={self.timezone}, coordinates={self.coordinates}, working_hours={self.working_hours})"

def validate_coordinates(coordinates):
    try:
        lat, lon = map(float, coordinates.split(','))
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Coordinates out of valid range")
        return coordinates
    except ValueError as e:
        raise ValueError(f"Invalid coordinates format: {e}")

def validate_working_hours(working_hours):
    try:
        start, end = map(int, working_hours.split('-'))
        if not (0 <= start < 24) or not (0 <= end < 24):
            raise ValueError("Working hours out of valid range")
        return working_hours
    except ValueError as e:
        raise ValueError(f"Invalid working hours format: {e}")

def load_team_members(config_path):
    try:
        # Load the configuration file
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        team_members = []
        for member in config.get('Team_Members', []):
            try:
                # Validate and create TeamMember object
                name = member['Name']
                timezone = member['Timezone']
                coordinates = validate_coordinates(member['Coordinates'])
                working_hours = validate_working_hours(member['Working_hours'])

                team_member = TeamMember(
                    name=name,
                    timezone=timezone,
                    coordinates=coordinates,
                    working_hours=working_hours
                )
                team_members.append(team_member)
            except KeyError as e:
                print(f"Missing attribute in team member: {e}")
            except ValueError as e:
                print(f"Invalid value for attribute: {e}")

        return team_members

    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {config_path}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
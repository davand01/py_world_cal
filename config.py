import json

def load_base_radius(config_path):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        base_radius = int(config["Status_Circle_Radius"])
        return base_radius
    except KeyError:
        print("Error: 'Status_Circle_Radius' key not found in the configuration file. Using default value of 200000.")
        return 200000
    except ValueError:
        print("Error: 'Status_Circle_Radius' value in the configuration file is not a valid integer.")
        return 200000

def load_map_height(config_path):
    try:
        # Load configuration from JSON file
        with open(config_path, 'r') as file:
            config = json.load(file)

        # Extract the map height
        map_height = int(config["Map_Height"])
        return map_height
    except KeyError:
        print("Error: 'Map_Height' key not found in the configuration file. Using default value of 500.")
        return 500  # Default height
    except ValueError:
        print("Error: 'Map_Height' value in the configuration file is not a valid integer.")
        return 500  # Default height
    
def load_team_name(config_path):
    try:
        # Load configuration from JSON file
        with open(config_path, 'r') as file:
            config = json.load(file)

        # Extract the map height
        team_name = str(config["Team_Name"])
        return team_name
    except KeyError:
        print("Error: 'Team_Name' key not found in the configuration file. Using default value: 'Team Awesome'.")
        return "Team Awesome"  # Default team name
    except ValueError:
        print("Error: 'Team_Name' value in the configuration file is not a valid string.")
        return "Team Awesome"  # Default team name

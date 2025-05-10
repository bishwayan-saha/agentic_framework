import json
JSON_FILE = "/home/bishwayansaha99/Python_Projects/adk/agent_with_a2a/registry.json"
def read_json():
    """Read the JSON file."""
    try:
        with open(JSON_FILE, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    finally:
        file.close()

def write_json(data):
    """Write data to the JSON file."""
    try:
        with open(JSON_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Exception {e}")
    finally:
        file.close()



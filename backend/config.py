import yaml
from typing import List, Dict

def load_config(config_path: str = 'config.yaml') -> List[Dict]:
    """Loads server configurations from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if not isinstance(config, list):
                raise ValueError("Configuration file should contain a list of servers.")
            for server in config:
                if not isinstance(server, dict) or 'name' not in server or 'glances_api_url' not in server:
                    raise ValueError("Each server in config should be a dictionary with 'name' and 'glances_api_url'.")
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration file: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid configuration format: {e}")

if __name__ == '__main__':
    try:
        servers_config = load_config()
        print("Configuration loaded successfully:")
        for server in servers_config:
            print(f"- {server['name']}: {server['glances_api_url']}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading configuration: {e}")
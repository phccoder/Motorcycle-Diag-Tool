# config_manager.py
import configparser

CONFIG_FILE = 'settings.ini'

def load_settings():
    """Loads settings from the INI file, creating it with defaults if it doesn't exist."""
    config = configparser.ConfigParser()
    # Provide default values
    config['DEFAULT'] = {
        'connection_mode': 'Simulator',
        'address': 'tcp://192.168.0.10:35000'
    }
    
    if not config.read(CONFIG_FILE):
        # If the file doesn't exist, create it with defaults
        save_settings({'connection_mode': 'Simulator', 'address': 'tcp://192.168.0.10:35000'})
        print("Settings file not found, creating with default values.")

    # Read the actual settings from the [OBD] section
    config.read(CONFIG_FILE)
    return dict(config['OBD'])

def save_settings(settings):
    """Saves the provided settings dictionary to the INI file."""
    config = configparser.ConfigParser()
    config['OBD'] = settings
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    print("Settings saved.")
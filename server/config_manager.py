import json
import os

CONFIG_FILE = 'blink_config.json'
DEFAULT_THRESHOLD = 34

class ConfigManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._create_default_config()
        return self._create_default_config()

    def _create_default_config(self):
        config = {
            'threshold': DEFAULT_THRESHOLD
        }
        self._save_config(config)
        return config

    def _save_config(self, config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

    def get_threshold(self):
        return self.config.get('threshold', DEFAULT_THRESHOLD)

    def set_threshold(self, threshold):
        self.config['threshold'] = threshold
        self._save_config(self.config) 
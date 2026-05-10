import json
import os

class ConfigLoader:
    """YAML/JSON ayarlarını sisteme yükler"""
    def __init__(self, config_path="data/config/settings.json"):
        self.config_path = config_path
        
    def load(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

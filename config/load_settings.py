import json

def setup(filePath='config/settings.json'):
    with open(filePath, 'r') as f:
        return json.load(f)
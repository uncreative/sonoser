import datetime
import json


# noinspection PyUnusedLocal
def _different_default_json_encoder(self, obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    return _different_default_json_encoder.default(obj)


# remember original json encoder
_different_default_json_encoder.default = json.JSONEncoder().default
# monkey patch json encoder's default function to above
json.JSONEncoder.default = _different_default_json_encoder

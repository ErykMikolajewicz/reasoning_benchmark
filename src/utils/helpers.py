import hashlib
import json

from chess import BLACK, WHITE

colors_strings_dict = {WHITE: "white", BLACK: "black"}


def color_to_string(color):
    color_string = colors_strings_dict[color]
    return color_string


def hash_dict(dict_) -> str:
    dict_str = json.dumps(dict_, sort_keys=True)
    hash_obj = hashlib.sha256(dict_str.encode("utf-8"))
    hash_str = hash_obj.hexdigest()
    return hash_str


models_short_name = {
    "anthropic-claude-opus-4-20250514": "claude-opus-4",
    "anthropic-claude-sonnet-4-20250514": "claude-sonnet-4",
    "gemini-gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-gemini-2.5-flash": "gemini-2.5-flash",
    "deepseek-deepseek-reasoner": "deepseek-reasoner",
}


def get_model_shorter_name(name: str):
    try:
        short_name = models_short_name[name]
        return short_name
    except KeyError:
        return name

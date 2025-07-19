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

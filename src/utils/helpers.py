from chess import WHITE, BLACK

colors_strings_dict = {WHITE: "white", BLACK: "black"}


def color_to_string(color):
    color_string = colors_strings_dict [color]
    return color_string

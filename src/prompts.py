main_prompt = """
You will be playing chess. Each time, you will receive a text representation of board. You will also be informed which color you are playing. Your task will be to make a move."""

extraction_prompt = """
Extract user move from text, and return it in san format, in json, example:
{"san":"c4"}"""

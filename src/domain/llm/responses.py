strategy = {
    "type": "json_schema",
    "json_schema": {
        "name": "chess_strategy",
        "schema": {
            "type": "object",
            "properties": {
                "strategy": {"type": "string"},
                "move": {
                    "type": "string",
                },
            },
            "required": ["strategy", "move"],
            "additionalProperties": False,
        },
    },
}

move = {
    "type": "json_schema",
    "json_schema": {
        "name": "chess_move",
        "schema": {
            "type": "object",
            "properties": {"move": {"type": "string"}},
            "required": ["move"],
            "additionalProperties": True,
        },
    },
}

class InvalidMove(BaseException):
    def __init__(self, invalid_move: str):
        self.invalid_move = invalid_move


class NoJsonInText(BaseException):
    def __init__(self, text: str):
        self.text = text

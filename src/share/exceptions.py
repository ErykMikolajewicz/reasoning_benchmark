class InvalidMove(BaseException):
    def __init__(self, invalid_move: str):
        self.invalid_move = invalid_move

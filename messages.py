class Messages:
    error = None
    msg = None

    def __init__(self, error: bool, msg: str):
        self.error = error
        self.msg = msg



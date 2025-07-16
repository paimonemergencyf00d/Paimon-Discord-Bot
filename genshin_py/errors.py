import genshin


class UserDataNotFound(Exception):
    """Exception when the robot database cannot find the user data"""

    pass


class GenshinAPIException(Exception):
    """Exception used to wrap genshin.py exceptions

    Attributes
    -----
    origin: `genshin.GenshinException`
    Exception thrown from genshin.py
    message: `str`
    Error message for robot users
    """

    origin: genshin.GenshinException
    message: str = ""

    def __init__(self, exception: genshin.GenshinException, message: str) -> None:
        self.origin = exception
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message}\n```{repr(self.origin)}```"

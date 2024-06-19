"""Module with custom exceptions."""


class NoRootFolderException(Exception):
    """Exception raised if no root folder is found in the user's folder
    directory on Google's Earth Engine.

    Attributes:
        message: explanation of the error
    """
    def __init__(
            self,
            message="Your Earth Engine account does not contain a root " +
            "folder. \n Create a home folder and try again."):
        self.message = message
        super().__init__(self.message)


class NoInternetConnectionError(Exception):
    """Exception raised when no internet connection is present on the user's
    side.

    Attributes:
        message: explanation of the error
    """
    def __init__(
            self,
            message="Seems that you are not connected to the Internet." +
            "\nFix your internet connection and try again."):
        self.message = message
        super().__init__(self.message)


class MessageNotFoundException(Exception):
    """Exception raised when message to be called (e.g. for display)
    is not found

    Attributes:
        msg_name: Name of the message that could not be found
        message: explanation of the error
    """
    def __init__(
            self,
            msg_name: str,
            message="Message {msg_name} could not be found."):
        self.message = message.format(msg_name)
        super().__init__(self.message)

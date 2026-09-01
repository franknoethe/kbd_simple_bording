class ApiError(Exception):
    """Raised by service functions to signal an error response with a status code."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

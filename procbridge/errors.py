class ErrorMessages:
    UNRECOGNIZED_PROTOCOL = 'unrecognized protocol'
    INCOMPATIBLE_VERSION = 'incompatible protocol version'
    INCOMPLETE_DATA = 'incomplete data'
    INVALID_STATUS_CODE = 'invalid status code'
    INVALID_BODY = 'invalid body'
    UNKNOWN_SERVER_ERROR = 'unknown server error'


class ProtocolError(Exception):
    def __init__(self, message: str, detail: str = None):
        self.message = message
        self.detail = detail


class ServerError(Exception):
    def __init__(self, message: str):
        self.message = message

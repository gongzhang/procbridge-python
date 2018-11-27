from enum import Enum


class Versions(Enum):
    V1_0 = b'\x01\x00'
    V1_1 = b'\x01\x01'

    @staticmethod
    def current():
        return Versions.V1_1


class StatusCode(Enum):
    REQUEST = 0
    GOOD_RESPONSE = 1
    BAD_RESPONSE = 2


class Keys(Enum):
    METHOD = 'method'
    PAYLOAD = 'payload'
    MESSAGE = 'message'

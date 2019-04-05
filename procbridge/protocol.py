import socket
import json
from typing import Any

from .const import StatusCode, Keys, Versions
from .errors import ProtocolError, ErrorMessages


def read_bytes(s: socket.socket, count: int) -> bytes:
    rst = b''
    if count == 0:
        return rst
    while True:
        tmp = s.recv(count - len(rst))
        if len(tmp) == 0:
            break
        rst += tmp
        if len(rst) == count:
            break
    return rst


def read_socket(s: socket.socket) -> (int, dict):
    # 1. FLAG 'pb'
    flag = read_bytes(s, 2)
    if flag != b'pb':
        raise ProtocolError(ErrorMessages.UNRECOGNIZED_PROTOCOL)

    # 2. VERSION
    ver = read_bytes(s, 2)
    if ver != Versions.current().value:
        raise ProtocolError(ErrorMessages.INCOMPATIBLE_VERSION,
                            "need version {} but found {}".format(Versions.current(), ver))

    # 3. STATUS CODE
    status_code = read_bytes(s, 1)
    if len(status_code) != 1:
        raise ProtocolError(ErrorMessages.INCOMPLETE_DATA)
    code = status_code[0]

    # 4. RESERVED (2 bytes)
    reserved = read_bytes(s, 2)
    if len(reserved) != 2:
        raise ProtocolError(ErrorMessages.INCOMPLETE_DATA)

    # 5. LENGTH (4-byte, little endian)
    len_bytes = read_bytes(s, 4)
    if len(len_bytes) != 4:
        raise ProtocolError(ErrorMessages.INCOMPLETE_DATA)
    json_len = len_bytes[0]
    json_len += len_bytes[1] << 8
    json_len += len_bytes[2] << 16
    json_len += len_bytes[3] << 24

    # 6. JSON OBJECT
    text_bytes = read_bytes(s, json_len)
    if len(text_bytes) != json_len:
        raise ProtocolError(ErrorMessages.INCOMPLETE_DATA,
                            'expect ' + str(json_len) + ' bytes but found ' + str(len(text_bytes)))
    try:
        obj = json.loads(str(text_bytes, encoding='utf-8'), encoding='utf-8')
    except Exception as err:
        raise ProtocolError(ErrorMessages.INVALID_BODY, "{}".format(err))

    return code, obj


def write_socket(s: socket.socket, status_code: StatusCode, json_obj: dict):
    # 1. FLAG
    s.sendall(b'pb')
    # 2. VERSION
    s.sendall(Versions.current().value)
    # 3. STATUS CODE
    s.sendall(bytes([status_code.value]))
    # 4. RESERVED 2 BYTES
    s.sendall(b'\x00\x00')

    # 5. LENGTH (little endian)
    json_text = json.dumps(json_obj)
    json_bytes = bytes(json_text, encoding='utf-8')
    len_bytes = len(json_bytes).to_bytes(4, byteorder='little')
    s.sendall(len_bytes)

    # 6. JSON
    s.sendall(json_bytes)


def write_request(s: socket.socket, method: str, payload: Any):
    body = {}
    if method is not None:
        body[Keys.METHOD.value] = method
    if payload is not None:
        body[Keys.PAYLOAD.value] = payload
    write_socket(s, StatusCode.REQUEST, body)


def write_good_response(s: socket.socket, payload: Any):
    body = {}
    if payload is not None:
        body[Keys.PAYLOAD.value] = payload
    write_socket(s, StatusCode.GOOD_RESPONSE, body)


def write_bad_response(s: socket.socket, message: str):
    body = {}
    if message is not None:
        body[Keys.MESSAGE.value] = message
    write_socket(s, StatusCode.BAD_RESPONSE, body)


def read_request(s: socket.socket) -> (str, Any):
    status_code, obj = read_socket(s)
    if status_code != StatusCode.REQUEST.value:
        raise ProtocolError(ErrorMessages.INVALID_STATUS_CODE, "{}".format(status_code))
    method = None
    payload = None
    if Keys.METHOD.value in obj:
        method = str(obj[Keys.METHOD.value])
    if Keys.PAYLOAD.value in obj:
        payload = obj[Keys.PAYLOAD.value]
    return method, payload


def read_response(s: socket.socket) -> (StatusCode, Any):
    status_code, obj = read_socket(s)
    if status_code == StatusCode.GOOD_RESPONSE.value:
        if Keys.PAYLOAD.value not in obj:
            return StatusCode.GOOD_RESPONSE, None
        else:
            return StatusCode.GOOD_RESPONSE, obj[Keys.PAYLOAD.value]
    elif status_code == StatusCode.BAD_RESPONSE.value:
        if Keys.MESSAGE.value not in obj:
            return StatusCode.BAD_RESPONSE, ErrorMessages.UNKNOWN_SERVER_ERROR
        else:
            return StatusCode.BAD_RESPONSE, str(obj[Keys.MESSAGE.value])
    else:
        raise ProtocolError(ErrorMessages.INVALID_STATUS_CODE, "{}".format(status_code))

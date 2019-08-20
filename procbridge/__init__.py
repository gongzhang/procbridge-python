import threading
import socket
from . import protocol as p
from typing import Any, Callable
from .errors import ProtocolError, ServerError
from .const import StatusCode, Versions

__all__ = ["Server", "Client", "Versions", "ProtocolError", "ServerError"]


class Client:

    def __init__(self, host: str, port: int):
        self.family = socket.AF_INET
        self.host = host
        self.port = port
        self.path = None

    @classmethod
    def from_unix(cls, path: str):
        ins = cls('', 0)
        ins.family = socket.AF_UNIX
        ins.path = path
        return ins

    @classmethod
    def from_inet(cls, host: str, port: int):
        return cls(host, port)

    def request(self, method: str, payload: Any = None) -> Any:
        if self.family == socket.AF_UNIX:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(self.path)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
        try:
            p.write_request(s, method, payload)
            code, result = p.read_response(s)
            if code == StatusCode.GOOD_RESPONSE:
                return result
            else:
                raise ServerError(result)
        finally:
            s.close()


class Server:

    def __init__(self, host: str, port: int, delegate: Callable[[str, Any], Any]):
        self.family = socket.AF_INET
        self.host = host
        self.port = port
        self.path = None
        self.started = False
        self.lock = threading.Lock()
        self.socket = None
        self.delegate = delegate

    @classmethod
    def from_unix(cls, path: str, delegate: Callable[[str, Any], Any]):
        ins = cls('', 0, delegate)
        ins.family = socket.AF_UNIX
        ins.path = path
        return ins

    @classmethod
    def from_inet(cls, host: str, port: int, delegate: Callable[[str, Any], Any]):
        return cls(host, port, delegate)

    def start(self, daemon=True):
        self.lock.acquire()
        try:
            if self.started:
                return

            if self.family == socket.AF_UNIX:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind(self.path)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind((self.host, self.port))
            self.socket.listen(0)
            t = threading.Thread(target=_start_server_listener, args=(self,), daemon=daemon)
            t.start()
            self.started = True
        except OSError as err:
            self.socket.close()
            raise err
        finally:
            self.lock.release()

    def stop(self):
        self.lock.acquire()
        try:
            if not self.started:
                return
            self.socket.close()
            self.socket = None
            self.started = False
        finally:
            self.lock.release()


def _start_server_listener(server: Server):
    try:
        while True:
            server.lock.acquire()
            if not server.started:
                return
            server.lock.release()

            # assert started == true:
            conn, _ = server.socket.accept()
            t = threading.Thread(target=_start_connection, args=(server, conn,), daemon=True)
            t.start()
    except ConnectionAbortedError:
        # socket stopped
        pass


def _start_connection(server: Server, s: socket.socket):
    try:
        method, payload = p.read_request(s)
        try:
            result = server.delegate(method, payload)
            p.write_good_response(s, result)
        except Exception as err:
            p.write_bad_response(s, str(err))
    except Exception as err:
        pass
    finally:
        s.close()

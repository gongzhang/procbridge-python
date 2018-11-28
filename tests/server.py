import time
import procbridge as pb

PORT = 8000


def delegate(method, payload):
    if method == 'echo':
        return payload
    elif method == 'sum':
        return sum(x for x in payload)
    elif method == 'err':
        raise RuntimeError("generated error")
    elif method == 'sleep':
        time.sleep(payload)


if __name__ == '__main__':
    s = pb.Server('0.0.0.0', PORT, delegate)
    s.start(daemon=False)
    print("Test Server is on {}...".format(PORT))

# procbridge-python

ProcBridge is a super-lightweight IPC (Inter-Process Communication) protocol over TCP socket or Unix domain socket. It enables you to **send and recieve JSON** between processes easily. ProcBridge is much like a simplified version of HTTP protocol, but only transfer JSON values.

Please note that this repo is the **Python implementation** of ProcBridge protocol. You can find detailed introduction of ProcBridge protocol in the main repository: [gongzhang/procbridge](https://github.com/gongzhang/procbridge).

# Installation

```
pip install procbridge==1.2.2
```

# Example

Server Side:

```python
import procbridge as pb

def delegate(method, args):
  
    # define remote methods:
    if method == 'echo':
        return args
        
    elif method == 'sum':
        return sum(x for x in args)
        
    elif method == 'err':
        raise RuntimeError("an server error")


if __name__ == '__main__':
    PORT = 8000
    s = pb.Server('0.0.0.0', PORT, delegate)
    s.start(daemon=False)
    print("Server is on {}...".format(PORT))
```

Client Side:

```python
import procbridge as pb
client = pb.Client('127.0.0.1', 8000)

# call remote methods:
client.request("echo", 123) # 123
client.request("echo", ['a', 'b', 'c']) # ['a', 'b', 'c']
client.request("sum", [1, 2, 3, 4]) # 10
```

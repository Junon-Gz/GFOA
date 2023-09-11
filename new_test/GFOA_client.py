from socket import socket,AF_INET,SOCK_STREAM
import json
def con_server(ip:str,port:int):
    try:
        sock = socket(AF_INET,SOCK_STREAM)
        sock.connect((ip,port))
    except Exception as e:
        sock = None
        print(f"连接服务端异常:{e}")
    finally:
        return sock

def send_msg(sock:socket,msg):
    try:
        sock.sendall(msg)
        data = sock.recv(1024)
        print(f"收到消息{data.decode('utf8')}")
    except Exception as e:
        print(f"消息异常:{e}")

if __name__ == "__main__":
    s = con_server('127.0.0.1',20000)
    data = {"yyb":"123","gs":"222"}
    msg = '暂停抢单' + json.dumps(data)
    send_msg(s,msg.encode('utf8'))


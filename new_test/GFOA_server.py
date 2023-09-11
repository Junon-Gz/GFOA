#创建服务端
#接收连接消息
#改变控制器值
#启动进程

import time
from socket import socket,AF_INET,SOCK_STREAM
from multiprocessing import Process,Queue
def echo_handler(address,client_sock:socket,flag):
    print('Got connection from {}'.format(address))
    try:
        msg = client_sock.recv(8192)
        cont = msg.decode('utf8')
        if "开始抢单" in cont:
            flag.value = True
            resend = '开始抢单成功'
            client_sock.sendall(resend.encode('utf8'))
        elif "暂停抢单" in cont:
            flag.value = False
            resend = '暂停抢单成功'
            client_sock.sendall(resend.encode('utf8'))
    except Exception as e:
        print(f"消息异常:{e}")
    finally:
        client_sock.close()

def echo_server(address,q,backlog=5):
    sock = socket(AF_INET,SOCK_STREAM)
    # sock = socket()
    sock.bind(address)
    sock.listen(backlog)
    while True:
        client_sock,client_addr = sock.accept()
        print("接收到监听")
        echo_handler(client_addr,client_sock,q)

def test(flag):
    while True:
        #开始/停止抢单控制器
        if flag.value:
            print(time.time())
            for i in range(10):
                print(i)
                time.sleep(2)

def start():
    snatch_queue = Queue()
    # q = Process(target=test,args=[snatch_queue])
    # q.start()
    p = Process(target=echo_server,args=[('127.0.0.1',20000),snatch_queue])
    p.start()


if __name__ == "__main__":
    import multiprocessing
    #开始/停止抢单标识
    share_val = multiprocessing.Value('b',False)
    # snatch_queue = Queue()
    Process(target=test,args=[share_val]).start()
    Process(target=test,args=[share_val]).start()
    Process(target=echo_server,args=[('127.0.0.1',20000),share_val]).start()
    print('结束')

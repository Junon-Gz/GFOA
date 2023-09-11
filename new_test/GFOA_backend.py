import argparse,os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",default=18888, type=int, nargs='?')
    return parser.parse_args()

from utils import log_record
logger =log_record.Logger(os.getcwd()+'/log/backend.log',level='debug').logger

import time,json
from socket import socket,AF_INET,SOCK_STREAM
from multiprocessing import Process,Queue
import multiprocessing
def echo_handler(address,client_sock:socket,flag):
    #处理客户端连接
    logger.info('Got connection from {}'.format(address))
    try:
        msg = client_sock.recv(8192)
        cont = msg.decode('utf8')
        if "开始抢单" in cont:
            flag.value = True
            resend = '开始抢单成功'
            client_sock.sendall(resend.encode('utf8'))
            data = json.loads(cont.replace("开始抢单",""))
            logger.info(f"开始抢单数据{data}")
        elif "暂停抢单" in cont:
            flag.value = False
            resend = '暂停抢单成功'
            client_sock.sendall(resend.encode('utf8'))
    except Exception as e:
        logger.info(f"后端socket消息异常:{e}")
    finally:
        client_sock.close()


def echo_server(address,q,backlog=5):
    #启动socket服务端
    sock = socket(AF_INET,SOCK_STREAM)
    sock.bind(address)
    sock.listen(backlog)
    while True:
        client_sock,client_addr = sock.accept()
        logger.info("接收到监听")
        echo_handler(client_addr,client_sock,q)

def test(flag):
    '''
    flag:启动/暂停抢单控制器(全局)
    '''
    #代替功能(抢单)函数
    while True:
        #开始/停止抢单控制器
        if flag.value:
            logger.info(time.time())
            for i in range(10):
                logger.info(i)
                time.sleep(2)

if __name__ == "__main__":
    args  = parse_args()
    #开始/停止抢单标识
    share_val = multiprocessing.Value('b',False)
    # snatch_queue = Queue()
    test1 = Process(target=test,args=[share_val])
    test2 = Process(target=test,args=[share_val])
    test3 = Process(target=echo_server,args=[('127.0.0.1',args.port),share_val])
    test1.start()
    test2.start()
    test3.start()
    logger.info('结束')
    test1.join()
    test2.join()
    test3.join()
    


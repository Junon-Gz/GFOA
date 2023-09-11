from socket import socket,AF_INET,SOCK_STREAM
import os,sys,subprocess,time
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor


import tkinter

from utils import tk_front,log_record
logger =log_record.Logger(os.getcwd()+'/log/front.log',level='debug').logger

def con_server(ip:str,port:int):
    try:
        sock = socket(AF_INET,SOCK_STREAM)
        sock.connect((ip,port))
    except Exception as e:
        sock = None
        logger.info(f"连接服务端异常:{e}")
    finally:
        return sock

def send_msg(sock:socket,msg):
    try:
        sock.sendall(msg)
        data = sock.recv(1024)
        logger.info(f"收到消息{data}")
    except Exception as e:
        logger.info(f"前端socket消息异常:{e}")

def taskkill(port):
    # 杀死原有的进程
    for i in [port]:
        with os.popen('netstat -aon|findstr "{}"|findstr LISTENING'.format(i)) as p:
            lines = p.read().split("\n")
            for line in lines:
                if "LISTENING" in line:
                    pid = line[line.index("LISTENING") + 9:].strip()
                    os.system("taskkill -pid {} -f".format(pid))


def net_is_used(port, ip='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        # logger.info('%s:%d is used' % (ip,port))
        return True
    except:
        # logger.info('%s:%d is unused' % (ip,port))
        return False


def run_backend(port):
    sleepTimes = 0
    #启动服务端
    p_http = subprocess.Popen([sys.executable, "-u", os.path.dirname(__file__) + os.sep + "GFOA_backend.py" , "--port" , str(port)])
    while True:
        #检查服务端是否启动成功
        if net_is_used(port) or sleepTimes > 10:
            # logger.debug("APP后台启动成功")
            break
        else:
            # logger.debug("等待APP后台启动...%s" % sleepTimes)
            time.sleep(0.5)
            sleepTimes = sleepTimes + 1
    p_http.wait()

def on_closing():
    logger.info("进程池结束")
    p1.terminate()
    p2.terminate()
    p3.terminate()
    # 关闭进程池
    # executor.shutdown()
    # 退出 tkinter 程序
    root.destroy()


######################backend######################
import json

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
            for i in range(3):
                logger.info(i)
                time.sleep(2)



if __name__ == "__main__":
    import multiprocessing
    # from multiprocessing import freeze_support
    # freeze_support()
    share_val = multiprocessing.Value('b',False)
    port = 20000
    taskkill(port)
    p1 = multiprocessing.Process(target=echo_server,args=[('127.0.0.1',port),share_val])
    p2 = multiprocessing.Process(target=test,args=[share_val])
    p3 = multiprocessing.Process(target=test,args=[share_val])
    p1.start()
    p2.start()
    p3.start()
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     app1 = executor.submit(echo_server,[('127.0.0.1',port),share_val])
    #     app2 = executor.submit(test,share_val)
    #     app3 = executor.submit(test,share_val)
    root=tkinter.Tk()
    root.title('GFOA')
    root.resizable(0,0)
    tk_front.buju(root,port)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
